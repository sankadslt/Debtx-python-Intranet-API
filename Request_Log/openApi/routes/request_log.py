"""
API : INC -1P08
Name : Create SLT Order
Description : Place SLT Order (Request Log API)
Created By : Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP :  request_id
      case_id
      order_id
      account_num
      parameters
      request_status
      request_status_description
          
OP : None
*/
"""

"""
    Version: Python 3.12.4
    Dependencies: Library
    Related Files: request-log.py, request_log_class.py
    Purpose: 
    Version:
        version: 1.0
        Last Modified Date: 2024-03-30
        Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)  
        Changes:     

    Notes:
"""

import logging
from fastapi import APIRouter, Body, HTTPException
from http import HTTPStatus
from datetime import datetime
from pymongo.errors import PyMongoError
from utils.database.connectDB import get_db_connection
from openApi.models.request_log_class import Request_Log_Model, Order_Details_Model
from utils.exceptions_handler.custom_exception_handle import DatabaseError, ValidationError, NotFoundError
from pydantic import ValidationError
import mysql.connector

router = APIRouter()
logger = logging.getLogger("INTRANET_PROCESS")
db = get_db_connection()

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="drs",
)

if conn.is_connected():
    print("Connected to MySQL database")
cursor = conn.cursor(dictionary=True)

#The collections
request_log_collection = "Request_Log"
request_error_log_collection = "Request_Error_Log"
order_details_collection = "Order_Details"
request_progress_log_collection = "Request_Progress_Log"
case_details_collection = "Case_details"

@router.post("/Create_SLT_Order", summary="Request Log", description="""**Mandatory Fields**<br><br>
       `case_id` <br>`order_id` <br> `account_num` <br> `parameters` (array) <br>`request_status`<br><br>
        **Optional Fields**<br><br>`request_id` <br>`request_status_description` <br> 
        <br><br> Valid request_status : "Open", "Complete" <br><br>**Conditions:**<br><br>  1. If order_id is 1, then parameters should have "incident_id" key.<br>
               2. If order_id is 2, then parameters should have "case_id", "start_date", "end_date", "case phase" and "settlement id" keys.<br>
               3. If order_id is 3, then parameters should have "case_id" and "cancel_reason" key<br>
               4. If order_id is 4, then parameters should have "case_id" and "end_date" key.<br>""")
async def request_log(request:Request_Log_Model):
    logger.info("INC -1P08 - Request Log - Details recieved")

    try:
        case_id = request.case_id

        # case_id is not empty
        if not case_id:
            logger.error("INC -1P08 - Request Log - case_id is empty")

            error_log = request.model_dump()
            error_log["request_status"] = "Error"
            error_log["request_status_description"] = "case_id is empty"
            error_log["created_dtm"] = datetime.now()

            cursor.execute("""
                INSERT INTO request_error_log (case_id, account_num, order_id, request_status, request_status_description, created_dtm)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (request.case_id, request.account_num, request.order_id, "Error", "case_id is empty", error_log["created_dtm"]))
            conn.commit()
            logger.info("INC -1P08 - Request Log - Details added successfully to error log db")
            return "case_id is empty"

        logger.info("INC -1P08 - Request Log - Checking if the case ID exists in the database")
        cursor.execute("SELECT * FROM case_details WHERE case_id = %s", (case_id,))
        existing_case = cursor.fetchone()

        if not existing_case:
            logger.error(f"INC -1P08 - Request Log - Case ID {case_id} does not exist in the database.")

            error_log = request.model_dump()
            error_log["request_status"] = "Error"
            error_log["request_status_description"] = f"Case ID {case_id} does not exist in the database."
            error_log["created_dtm"] = datetime.now()

            cursor.execute("""
                INSERT INTO request_error_log (case_id, account_num, order_id, request_status, request_status_description, created_dtm)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (request.case_id, request.account_num, request.order_id, "Error", error_log["request_status_description"], error_log["created_dtm"]))
            conn.commit()
            logger.info("INC -1P08 - Request Log - Details added successfully to error log db")
            return "Case ID does not exist in the database."

        if not request.account_num:
            logger.error("INC -1P08 - Request Log - account_num is empty")
            error_log = request.model_dump()
            error_log["request_status"] = "Error"
            error_log["request_status_description"] = "account_num is empty"
            error_log["created_dtm"] = datetime.now()
            
            cursor.execute("""
                INSERT INTO request_error_log (case_id, account_num, order_id, request_status, request_status_description, created_dtm)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (request.case_id, request.account_num, request.order_id, "Error", "account_num is empty", error_log["created_dtm"]))
            conn.commit()
            return "account_num is empty"

        if len(request.account_num) != 10:
            logger.error("INC -1P08 - Request Log - account_num is not 10 digits")
            error_log = request.model_dump()
            error_log["request_status"] = "Error"
            error_log["request_status_description"] = "account_num is not 10 digits"
            error_log["created_dtm"] = datetime.now()

            cursor.execute("""
                INSERT INTO request_error_log (case_id, account_num, order_id, request_status, request_status_description, created_dtm)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (request.case_id, request.account_num, request.order_id, "Error", "account_num is not 10 digits", error_log["created_dtm"]))
            conn.commit()
            return "account_num is not 10 digits"

        if not request.order_id:
            logger.error("INC -1P08 - Request Log - order_id is empty")
            error_log = request.model_dump()
            error_log["request_status"] = "Error"
            error_log["request_status_description"] = "order_id is empty"
            error_log["created_dtm"] = datetime.now()

            cursor.execute("""
                INSERT INTO request_error_log (case_id, account_num, order_id, request_status, request_status_description, created_dtm)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (request.case_id, request.account_num, request.order_id, "Error", "order_id is empty", error_log["created_dtm"]))
            conn.commit()
            return "order_id is empty"

        request_id = 0

        if request.request_id:
            request_id = request.request_id
            logger.info("INC -1P08 - Request Log - Checking if the request ID already exists in the database")
            cursor.execute("SELECT * FROM request_log WHERE request_id = %s", (request.request_id,))
            existing_request_log = cursor.fetchone()

            if existing_request_log:
                logger.error(f"INC -1P08 - Request Log - Request ID {request.request_id} already exists in the database.")
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail=f"request_id: {request.request_id} already exists."
                )
        else:
            cursor.execute("SELECT request_id FROM request_log ORDER BY request_id DESC LIMIT 1")
            latest_request = cursor.fetchone()
            request_id = latest_request["request_id"] + 1 if latest_request else 1
            logger.info(f"INC -1P08 - Request Log - Generated new request ID: {request_id}")

        try:
            created_dtm = datetime.now()
            request_status_dtm = datetime.now()

            # Insert into request_log
            cursor.execute("""
                INSERT INTO request_log 
                (request_id, case_id, account_num, order_id, request_status, 
                request_status_description, request_status_dtm, created_dtm, doc_version)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request_id, case_id, request.account_num, request.order_id,
                "Open", None, request_status_dtm, created_dtm, "1.0"
            ))
            conn.commit()
            
            # Insert into request_log_details
            # Extract up to 10 parameters from the parameters 
            params = list(request.parameters.values()) if isinstance(request.parameters, dict) else list(request.parameters)

            # Ensure exactly 10 parameters (missing ones will be None)
            params = params[:10] + [None] * (10 - len(params))

            # Insert into request_details
            cursor.execute("""
                INSERT INTO request_log_details (
                    request_id, para_1, para_2, para_3, para_4, para_5,
                    para_6, para_7, para_8, para_9, para_10
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (request_id, *params))

            conn.commit()

            # Insert into request_progress_log
            cursor.execute("""
                INSERT INTO request_progress_log 
                (request_id, case_id, account_num, order_id, request_status, 
                request_status_description, request_status_dtm, created_dtm, doc_version)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request_id, case_id, request.account_num, request.order_id,
                "Open", None, request_status_dtm, created_dtm, "1.0"
            ))
            conn.commit()

            order_id = 0
            order_type = ""

            match request.order_id:
                case 1:
                    order_id = 1
                    order_type = "Cust Details for Case Registration"
                case 2:
                    order_id = 2
                    order_type = "Monitor Payment"
                case 3:
                    order_id = 3
                    order_type = "Monitor Payment Cancel"
                case 4:
                    order_id = 4
                    order_type = "Close Monitor If No Transaction"

            # Insert into order_details
            cursor.execute("""
                INSERT INTO order_details 
                (order_id, order_type, account_num, created_dtm, end_dtm, attempt_mode)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                order_id, order_type, request.account_num, datetime.now(), None, 5
            ))
            conn.commit()
            # str(request.parameters),

            logger.info("INC -1P08 - Request Log - Details added successfully to order details db")
            return {"message": "Request Log details added successfully"}

        except mysql.connector.Error as e:
            logger.error(f"INC -1P08 - Request Log - Database error during status update: {str(e)}")
            return HTTPException(status_code=500, detail="Failed to add details to the database.")
     
    except ValidationError as ve:
        logger.error(f"INC -1P08 - Request Log - Validation error: {str(ve)}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(ve))          
        
    except Exception as e:
        logger.error(f"INC -1P08 - Request Log - Unexpected error: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")   