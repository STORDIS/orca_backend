import ipaddress
from django.db import models
from django.forms import ValidationError


class ReDiscoveryConfig(models.Model):

    device_ip = models.CharField(max_length=64, primary_key=True)
    interval = models.IntegerField()
    last_discovered = models.DateTimeField(null=True)

    objects = models.Manager()


class IPRange(models.Model):
    range = models.CharField(max_length=64, primary_key=True)

    @staticmethod
    def delete_ip_range(range: str):
        """
        Delete the given IP range.
        
        Args:
            - range (str): The IP range to delete.
        Returns:
            None
        """
        try:
            ip_range = IPRange.objects.get(range=range)
            ip_range.delete()
            
            # Delete IPAvailability objects without a range
            IPAvailability.delete_ip_without_range()
        except IPRange.DoesNotExist:
            raise ValidationError(f"IP range {range} does not exist.")

    @staticmethod
    def add_ip_range(range: str):
        """
        Add a new IP range and associate the IPs with IPAvailability.
        
        Args:
            - range (str): The IP range to add.
        Returns:
            IPRange: The created IP range.
        """
        
        ips_to_add = get_ips_in_range(range)
        ip_range, _ = IPRange.objects.get_or_create(range=range)
        
        # Create IPAvailability objects and associate them with the IP range
        for ip in ips_to_add:
            ip_availability, _ = IPAvailability.objects.get_or_create(ip=ip)
            ip_availability.range.add(ip_range)
            
        return ip_range


class IPAvailability(models.Model):
    ip = models.CharField(max_length=64, primary_key=True)
    used_in = models.CharField(max_length=64, null=True)
    device_ip = models.CharField(max_length=64, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    range = models.ManyToManyField(IPRange)
    
    @staticmethod
    def delete_ip_without_range():
        """
        Delete IPAvailability objects without a range.
        
        Returns:
            None
        """
        ip_availability = IPAvailability.objects.filter(used_in__isnull=True, range__isnull=True)
        ip_availability.delete()
        
    @staticmethod
    def add_ip_usage(ip: str, device_ip: str, used_in: str):
        """
        Add IP usage information.
        
        Args:
            - ip (str): The IP address to add usage information for.
            - used_in (str): The name of the device using the IP.
        Returns:
            None
        """
        try:
            ip_availability = IPAvailability.objects.get(ip=ip.split("/")[0])
            ip_availability.used_in = used_in
            ip_availability.device_ip = device_ip
            ip_availability.save()
        except IPAvailability.DoesNotExist:
            raise ValidationError(f"IP {ip} does not exist.")
        
    @staticmethod
    def remove_usage_by_device_ip_and_used_in(device_ip: str, used_in: str):
        """
        Remove IP usage information by device IP and used in.
        
        Args:
            - device_ip (str): The device IP to remove usage information for.
            - used_in (str): The name of the device using the IP.
        Returns:
            None
        """
        IPAvailability.objects.filter(
            device_ip=device_ip, used_in=used_in
        ).update(device_ip=None, used_in=None)
        
        IPAvailability.delete_ip_without_range()

def get_ips_in_range(ip_range: str):
    """
    Generate a list of IPs in the provided range (supports CIDR and hyphenated ranges).
    
    Args:
        - ip_range (str): The IP range to generate IPs for.
    Returns:
        list: A list of IP addresses in the range.
    """
    if "/" in ip_range:
        # Handle CIDR notation (e.g., "192.168.1.0/24")
        ip_network = ipaddress.ip_network(ip_range, strict=True)
        if ip_network.prefixlen >= 24 and ip_network.prefixlen <= 32:
            return [
                str(ip) for ip in ip_network
            ]
        else:
            raise ValidationError("Invalid IP range format.")
    elif "-" in ip_range:
        # Handle hyphenated range (e.g., "192.168.1.1-.168.1.10")
        start_ip, end_ip = ip_range.split("-")
        start_ip = ipaddress.ip_address(start_ip.strip())
        end_ip = ipaddress.ip_address(end_ip.strip())

        return [
            str(ip) for generic_ip in ipaddress.summarize_address_range(start_ip, end_ip) for ip in generic_ip
        ]
    else:
        raise ValidationError("Invalid IP range format. Please use CIDR or hyphenated format.")
        