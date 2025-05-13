from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Literal, Optional, Union
from datetime import datetime
from utils.validators.dateTimeValidator import human_readable_dateTime_to_datetime
   

class Request_Log_Model(BaseModel):
    request_id: Optional[int] = Field(None, alias="request_id")
    created_dtm: Optional[datetime] = Field(None, description="Date and time when the request was created")
    case_id: Optional[int] = Field(None, description="case_id")
    order_id: int | None = None
    account_num: Optional[str] = Field(None, description="account number")
    parameters: dict[str, Union[str, datetime, int]] = Field(default_factory=list, description="List of additional parameters")
    request_status: Optional[Literal["Open", "Complete"]] = Field("Open", description="Status of the monitor")
    request_status_description: Optional[str]| None = None
    request_status_dtm: Optional[datetime] = Field(None, description="Date and time when the request status was updated")
    doc_version: str = "1.0"
    
    @field_validator("created_dtm", "request_status_dtm", mode='before')
    @classmethod
    def parse_effective_dtm(cls, value):
        return human_readable_dateTime_to_datetime(value)
    
    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, parameters: dict[str, str], info: ValidationInfo):
        order_id = info.data.get("order_id")  # Use info.data instead of values.get()

        if order_id == 1:
            required_keys = {"incident_id"}
        elif order_id == 2:
            required_keys = {"case_id", "start_date", "end_date","case_phase", "settlement_id"}
        elif order_id == 3:
            required_keys = {"case_id", "cancel_reason"}
        elif order_id == 4:
            required_keys = {"case_id", "end_date"}         
        else:
            return parameters  # Skip validation for other order_id values

        # Check for missing required keys
        missing_keys = required_keys - parameters.keys()
        if missing_keys:
            raise ValueError(f"Missing required keys {missing_keys} in parameters when order_id is {order_id}")
        
        extra_keys = parameters.keys() - required_keys
        if extra_keys:
            raise ValueError(f"Invalid keys {extra_keys} in parameters when order_id is {order_id}. "
                            f"Only {required_keys} are allowed.")
        
        if order_id == 2:
            parameters["start_date"] = cls.parse_effective_dtm(parameters["start_date"])
            parameters["end_date"] = cls.parse_effective_dtm(parameters["end_date"])
            
        elif order_id == 4:
            parameters["end_date"] = cls.parse_effective_dtm(parameters["end_date"])
        
        return parameters
    

class Order_Details_Model(BaseModel):
    order_id: int
    order_type: str
    account_num: str
    parameters: dict[str, Union[str, datetime, int]] = Field(default_factory=list, description="List of additional parameters")
    created_dtm: datetime
    end_dtm: Optional[datetime] = None
    attempt_mode: Literal[1,2,3,4,5]

    #validate datetime format
    @field_validator("created_dtm", "end_dtm", mode='before')
    @classmethod
    def parse_effective_dtm(cls, value):
        return human_readable_dateTime_to_datetime(value)