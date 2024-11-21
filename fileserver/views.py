import os

from django.forms import model_to_dict
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from fileserver.dhcp import get_dhcp_config, put_dhcp_config, get_dhcp_backup_file, get_dhcp_backup_files_list
from fileserver.models import DHCPServerDetails, DHCPDevices
from fileserver.ztp import get_ztp_files, add_ztp_file, delete_ztp_file
from log_manager.decorators import log_request
from log_manager.logger import get_backend_logger

_logger = get_backend_logger()


@api_view(["GET"])
@log_request
def download_file(request, filename):
    if request.method == "GET":
        app_directory = os.path.dirname(os.path.abspath(__file__))  # Get the path of the current app
        path = os.path.join(app_directory, 'media', filename)
        if os.path.exists(path):
            return FileResponse(open(path, "rb+"), as_attachment=True, filename=filename)
        else:
            return Response("File not found", status=status.HTTP_404_NOT_FOUND)


@api_view(["GET", "PUT", "DELETE"])
@log_request
def host_ztp_files(request):
    result = []
    http_status = True
    if request.method == "GET":
        filename = request.GET.get("filename", "")
        try:
            data = get_ztp_files(filename)
            return Response(data, status=status.HTTP_200_OK)
        except FileNotFoundError as e:
            _logger.error("File not found %s", e)
            return Response("File not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            _logger.error("Internal server error %s", e)
            return Response("Internal server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == "PUT":
        req_data_list = request.data if isinstance(request.data, list) else [request.data]
        for req_data in req_data_list:
            filename = req_data.get("filename")
            content = req_data.get("content")
            try:
                add_ztp_file(filename, content)
                result.append({"message": f"saved {filename} to ztp files", "status": "success"})
            except Exception as e:
                _logger.error(e)
                http_status = False
                result.append({"message": e, "status": "failed"})
    if request.method == "DELETE":
        req_data_list = request.data if isinstance(request.data, list) else [request.data]
        for req_data in req_data_list:
            filename = req_data.get("filename")
            try:
                delete_ztp_file(filename)
                result.append({"message": f"deleted {filename} from ztp files", "status": "success"})
            except Exception as e:
                _logger.error(e)
                http_status = False
                result.append({"message": e, "status": "failed"})
    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["GET", "PUT"])
def dhcp_config(request):
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip")
        if not device_ip:
            return Response(
                {"message": "Required field mgt_ip not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        dhcp_creds = DHCPServerDetails.objects.filter(device_ip=device_ip).first()
        if not dhcp_creds:
            return Response(
                {"message": "No credentials found for this device"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            file = get_dhcp_config(
                ip=device_ip, username=dhcp_creds.username, password=dhcp_creds.password
            )
            return Response({"content": file, "filename": "dhcpd.conf"}, status=status.HTTP_200_OK)
        except FileNotFoundError as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if request.method == "PUT":
        req_list = request.data if isinstance(request.data, list) else [request.data]
        for req_data in req_list:
            dhcp_creds = DHCPServerDetails.objects.filter(device_ip=req_data.get("mgt_ip")).first()
            if not dhcp_creds:
                return Response(
                    {"message": "No credentials found for this device"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                put_dhcp_config(
                    ip=req_data["mgt_ip"],
                    username=dhcp_creds.username,
                    password=dhcp_creds.password,
                    content=req_data["content"],
                )
                result.append({"message": f"{request.method} request successful", "status": "success"})
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                http_status = False
                result.append({"message": str(e), "status": "failed"})
        return Response(
            data={"result": result},
            status=status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET", "PUT", "DELETE"])
@log_request
def dhcp_credentials(request):
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip")
        if device_ip:
            data = DHCPServerDetails.objects.filter(device_ip=device_ip).first()
            details = model_to_dict(data) if data else None
        else:
            details = DHCPServerDetails.objects.all().values()
        return (
            Response(details, status=status.HTTP_200_OK)
            if details
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )

    if request.method == "PUT":
        req_data = request.data if isinstance(request.data, list) else [request.data]
        results = []
        for data in req_data:
            try:
                DHCPServerDetails.objects.update_or_create(
                    device_ip=data["mgt_ip"], defaults={
                        "username": data["username"],
                        "password": data["password"]
                    }
                )
                results.append({"message": f"{request.method} request successful", "status": "success"})
            except Exception as e:
                results.append({"message": str(e), "status": "failed"})
        return Response(results, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        req_data = request.data if isinstance(request.data, list) else [request.data]
        results = []
        for data in req_data:
            device_ip = data["mgt_ip"]
            if not device_ip:
                _logger.error("Required field device mgt_ip not found.")
                return Response(
                    {"message": "Required field device mgt_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            dhcp_obj = DHCPServerDetails.objects.filter(device_ip=device_ip).first()
            if dhcp_obj:
                dhcp_obj.delete()
                results.append({"message": f"{request.method} request successful", "status": "success"})
            else:
                results.append({"message": f"{request.method} request failed", "status": "failed"})
        return Response(results, status=status.HTTP_200_OK)


@api_view(["GET"])
@log_request
def dhcp_backup(request):
    if request.method == "GET":
        device_ip = request.GET.get("mgt_ip")
        if not device_ip:
            _logger.error("Required field device mgt_ip not found.")
            return Response(
                {"status": "Required field device mgt_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        dhcp_creds = DHCPServerDetails.objects.filter(device_ip=device_ip).first()
        try:
            filename = request.GET.get("filename", "")
            if filename:
                file = get_dhcp_backup_file(
                    ip=device_ip,
                    username=dhcp_creds.username,
                    password=dhcp_creds.password,
                    filename=filename
                )
                return Response({"content": file, "filename": filename}, status=status.HTTP_200_OK)
            else:
                files_list = get_dhcp_backup_files_list(
                    ip=device_ip,
                    username=dhcp_creds.username,
                    password=dhcp_creds.password
                )
                return Response(files_list, status=status.HTTP_200_OK)
        except FileNotFoundError as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@log_request
def get_dhcp_device(request):
    if request.method == "GET":
        try:
            result = DHCPDevices.objects.all().values()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"message": "File not found"}, status=status.HTTP_404_NOT_FOUND)


def _get_file_content(path, file_name):
    with open(path, "r") as f:
        return f.read()