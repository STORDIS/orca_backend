import ipaddress
import os

from django.forms import model_to_dict
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from fileserver.dhcp import get_dhcp_config, put_dhcp_config, get_dhcp_backup_file, get_dhcp_backup_files_list, \
    update_dhcp_access, delete_dhcp_backup_file, get_dhcp_auth_details
from fileserver.models import DHCPServerDetails
from fileserver import ztp, constants
from fileserver.tasks import scan_dhcp_leases_task
from log_manager.decorators import log_request
from log_manager.logger import get_backend_logger

_logger = get_backend_logger()


@api_view(["GET"])
@permission_classes([AllowAny])
def download_file(request, filepath=None):
    if request.method == "GET":
        _logger.info("Downloading file: %s", filepath)
        app_directory = os.path.dirname(os.path.abspath(__file__))  # Get the path of the current app
        path = os.path.join(app_directory, 'media/download', filepath)
        if os.path.isfile(path):
            return FileResponse(open(path, 'rb'), as_attachment=True, filename=filepath)
        elif os.path.isdir(path):
            return Response(
                [{
                    "filename": f, "path": f"files/download/{filepath}/{f}"
                } for f in os.listdir(path)
                    if os.path.isfile(os.path.join(path, f))],
                status=status.HTTP_200_OK
            )
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
            _logger.info("Getting ztp file: %s", filename)
            data = ztp.get_ztp_files(filename)
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
                _logger.info("Saving ztp file: %s", filename)
                ztp.add_ztp_file(filename, content)
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
                _logger.info("Deleting ztp file: %s", filename)
                ztp.delete_ztp_file(filename)
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
        device_ip = request.GET.get("device_ip")
        if not device_ip:
            _logger.error("Required field device_ip not found")
            return Response(
                {"message": "Required field device_ip not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        dhcp_creds = DHCPServerDetails.objects.filter(device_ip=device_ip).first()
        if not dhcp_creds:
            _logger.error("No credentials found for this device")
            return Response(
                {"message": "No credentials found for this device"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            _logger.info(f"Getting DHCP config for {device_ip}")
            file = get_dhcp_config(
                ip=device_ip, username=dhcp_creds.username
            )
            return Response(file, status=status.HTTP_200_OK)
        except FileNotFoundError as e:
            _logger.error("File not found %s", e)
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            _logger.error("Internal server error %s", e)
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if request.method == "PUT":
        req_list = request.data if isinstance(request.data, list) else [request.data]
        for req_data in req_list:
            dhcp_creds = DHCPServerDetails.objects.filter(device_ip=req_data.get("device_ip")).first()
            if not dhcp_creds:
                return Response(
                    {"message": "No credentials found for this device"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                _logger.info(f"Updating DHCP config for {req_data['device_ip']}")
                output, error = put_dhcp_config(
                    ip=req_data["device_ip"],
                    username=dhcp_creds.username,
                    content=req_data["content"],
                )
                if error:
                    _logger.error(error)
                    result.append({"message": error, "status": "failed"})
                    http_status = False
                else:
                    _logger.info(output)
                    result.append({"message": f"{request.method} request successful", "status": "success"})
            except Exception as e:
                import traceback
                _logger.error(traceback.format_exc())
                _logger.error("Internal server error %s", e)
                http_status = False
                result.append({"message": str(e), "status": "failed"})
        return Response(
            data={"result": result},
            status=status.HTTP_200_OK if http_status else status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET", "PUT", "DELETE"])
@log_request
def dhcp_auth(request):
    http_status = True
    result = []
    if request.method == "GET":
        details = get_dhcp_auth_details()
        return (
            Response(model_to_dict(details), status=status.HTTP_200_OK)
            if details
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )

    if request.method == "PUT":
        req_data = request.data if isinstance(request.data, list) else [request.data]
        for data in req_data:
            _logger.info(f"Updating DHCP credentials for {data['device_ip']}")
            device_ip = data.get("device_ip")
            if not device_ip:
                _logger.error("Required field device_ip not found.")
                return Response(
                    {"message": "Required field device_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            username = data.get("username")
            if not username:
                _logger.error("Required field username not found.")
                return Response(
                    {"message": "Required field username not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            password = data.get("password", None)
            try:
                ipaddress.ip_address(device_ip)
            except Exception as e:
                _logger.error(e)
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            try:
                update_dhcp_access(device_ip, username, password)
                result.append({"message": f"{request.method} request successful", "status": "success"})
            except Exception as e:
                http_status = False
                result.append({"message": str(e), "status": "failed"})
    if request.method == "DELETE":
        req_data = request.data if isinstance(request.data, list) else [request.data]
        for data in req_data:
            device_ip = data["device_ip"]
            if not device_ip:
                _logger.error("Required field device_ip not found.")
                return Response(
                    {"message": "Required field device_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            _logger.info(f"Deleting DHCP Server details for {device_ip}")
            dhcp_obj = DHCPServerDetails.objects.filter(device_ip=device_ip).first()
            if dhcp_obj:
                dhcp_obj.delete()
            result.append({"message": f"{request.method} request successful", "status": "success"})
    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["GET", "DELETE"])
@log_request
def dhcp_backup(request):
    result = []
    http_status = True
    if request.method == "GET":
        device_ip = request.GET.get("device_ip")
        if not device_ip:
            _logger.error("Required field device_ip not found.")
            return Response(
                {"status": "Required field device_ip not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        dhcp_creds = DHCPServerDetails.objects.filter(device_ip=device_ip).first()
        try:
            _logger.info(f"Getting DHCP backup files for {device_ip}")
            filename = request.GET.get("filename", "")
            if filename:
                file = get_dhcp_backup_file(
                    ip=device_ip,
                    username=dhcp_creds.username,
                    filename=filename
                )
                return Response({"content": file, "filename": filename}, status=status.HTTP_200_OK)
            else:
                _logger.info(f"Getting DHCP backup files list for {device_ip}")
                files_list = get_dhcp_backup_files_list(
                    ip=device_ip,
                    username=dhcp_creds.username,
                )
                return Response(files_list, status=status.HTTP_200_OK)
        except FileNotFoundError as e:
            _logger.error(e)
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            _logger.error(e)
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if request.method == "DELETE":
        req_data = request.data if isinstance(request.data, list) else [request.data]
        for req in req_data:
            device_ip = req.get("device_ip")
            if not device_ip:
                _logger.error("Required field device_ip not found.")
                return Response(
                    {"status": "Required field device_ip not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            _logger.info(f"Deleting DHCP backup files for {device_ip}")
            try:
                dhcp_creds = DHCPServerDetails.objects.filter(device_ip=device_ip).first()
                output, error = delete_dhcp_backup_file(
                    ip=device_ip,
                    username=dhcp_creds.username,
                    file_name=req.get("filename", "")
                )
                if error:
                    http_status = False
                    _logger.error(error)
                    result.append({"message": error, "status": "failed"})
                else:
                    _logger.info(output)
                result.append({"message": f"{request.method} request successful", "status": "success"})
            except Exception as e:
                _logger.error(e)
                http_status = False
                result.append({"message": str(e), "status": "failed"})
    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

@api_view(["GET"])
def get_templates(request):
    if request.method == "GET":
        try:
            _logger.info("Getting templates")
            app_directory = os.path.dirname(os.path.abspath(__file__))
            template_directory = os.path.join(app_directory, constants.templates_path)
            files = []
            for file in os.listdir(template_directory):
                with open(os.path.join(template_directory, file), "r") as f:
                    files.append({"filename": file, "content": f.read()})
            return Response(files, status=status.HTTP_200_OK) if files else Response(status=status.HTTP_204_NO_CONTENT)
        except FileNotFoundError as e:
            _logger.error(e)
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            _logger.error(e)
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
@log_request
def rename_ztp_file(request):
    result = []
    http_status = True
    if request.method == "PUT":
        req_list: list = request.data if isinstance(request.data, list) else [request.data]
        for req_data in req_list:
            _logger.info("Renaming ZTP file")
            old_filename = req_data.get("old_filename")
            new_filename = req_data.get("new_filename")
            if not old_filename:
                _logger.error("Required field filename not found.")
                return Response(
                    {"status": "Required field filename not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not new_filename:
                _logger.error("Required field new_filename not found.")
                return Response(
                    {"status": "Required field new_filename not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                ztp.rename_ztp_file(old_filename, new_filename)
                result.append({"message": f"{request.method} request successful", "status": "success"})
            except Exception as e:
                _logger.error(e)
                http_status = False
                result.append({"message": str(e), "status": "failed"})
    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["PUT"])
def scan_dhcp_leases(request):
    result = []
    http_status = True
    if request.method == "PUT":
        try:
            task = scan_dhcp_leases_task.apply_async()
            result.append({
                "task_id": task.task_id, "message": f"{request.method} request successful", "status": "success"
            })
        except Exception as e:
            _logger.error(e)
            http_status = False
            result.append({"message": str(e), "status": "failed"})
    return Response(
        {"result": result},
        status=status.HTTP_200_OK
        if http_status
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
    )