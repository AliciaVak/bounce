import sys, os

from flasgger import Swagger, swag_from

from business_logic.scheduler import Scheduler
from enums.machine_type import MachineType
from enums.operation_request_status import OperationRequestStatus
from error_handlers import register_error_handlers
from exceptions import BadRequestError
from models.operating_room import OperatingRoom
from models.operation_request import OperationRequest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from config import Config


load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)
swagger = Swagger(app)
register_error_handlers(app)

# create hospital
rooms = [
    OperatingRoom(id=1, machines={MachineType.MRI, MachineType.CT, MachineType.ECG}),
    OperatingRoom(id=2, machines={MachineType.CT, MachineType.ECG}),
    OperatingRoom(id=3, machines={MachineType.CT, MachineType.ECG}),
    OperatingRoom(id=4, machines={MachineType.MRI, MachineType.ECG}),
    OperatingRoom(id=5, machines={MachineType.MRI, MachineType.ECG}),
]
scheduler = Scheduler(operating_rooms=rooms)

@app.route('/schedule', methods=['POST'])
@swag_from('docs/schedule.yml')
def schedule_surgery():
    data = request.get_json()
    doctor_type_str = data.get("doctor_type")
    if not doctor_type_str:
        raise BadRequestError("Missing doctor_type in payload")
    operation_data: OperationRequest = scheduler.schedule(doctor_type_str)

    response = {
        "status": operation_data.status.value,
        "request_id": operation_data.id
    }

    if operation_data.scheduled_room_id:
        response.update({
            "room_id": operation_data.scheduled_room_id,
            "start_time": operation_data.scheduled_start_time.isoformat(),
            "end_time": operation_data.scheduled_end_time.isoformat(),
        })

    return jsonify(response), 200 if operation_data.status == OperationRequestStatus.SCHEDULED else 202



if __name__ == '__main__':
    app.run(debug=True, threaded=True)
