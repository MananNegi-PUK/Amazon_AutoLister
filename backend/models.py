import datetime
import uuid
from .database import MongoField, Base

class ModelBase:
    __tablename__ = ""
    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            
    def to_mongo(self):
        d = {}
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            d[k] = v
            
        # Map 'id' attribute to '_id' key for MongoDB
        if "id" in d:
            d["_id"] = d.pop("id")
        return d
        
    @classmethod
    def from_mongo(cls, doc):
        if not doc:
            return None
        d = doc.copy()
        # Map '_id' back to 'id' string representation
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
        return cls(**d)

class SourceFile(ModelBase):
    __tablename__ = "source_files"
    
    id = MongoField("id")
    file_type = MongoField("file_type")
    filename = MongoField("filename")
    filepath = MongoField("filepath")
    uploaded_at = MongoField("uploaded_at")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "uploaded_at"):
            self.uploaded_at = datetime.datetime.utcnow()

class LearnedMapping(ModelBase):
    __tablename__ = "learned_mappings"
    
    id = MongoField("id")
    amazon_attribute = MongoField("amazon_attribute")
    internal_column = MongoField("internal_column")
    confidence_score = MongoField("confidence_score")
    is_active = MongoField("is_active")
    updated_at = MongoField("updated_at")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "confidence_score"):
            self.confidence_score = 1.0
        if not hasattr(self, "is_active"):
            self.is_active = True
        if not hasattr(self, "updated_at"):
            self.updated_at = datetime.datetime.utcnow()

class ValueMapping(ModelBase):
    __tablename__ = "value_mappings"
    
    id = MongoField("id")
    amazon_attribute = MongoField("amazon_attribute")
    internal_value = MongoField("internal_value")
    amazon_value = MongoField("amazon_value")
    confidence_score = MongoField("confidence_score")
    updated_at = MongoField("updated_at")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "confidence_score"):
            self.confidence_score = 1.0
        if not hasattr(self, "updated_at"):
            self.updated_at = datetime.datetime.utcnow()

class HardcodedDefault(ModelBase):
    __tablename__ = "hardcoded_defaults"
    
    id = MongoField("id")
    amazon_attribute = MongoField("amazon_attribute")
    default_value = MongoField("default_value")
    is_active = MongoField("is_active")
    updated_at = MongoField("updated_at")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "is_active"):
            self.is_active = True
        if not hasattr(self, "updated_at"):
            self.updated_at = datetime.datetime.utcnow()

class AdminRule(ModelBase):
    __tablename__ = "admin_rules"
    
    id = MongoField("id")
    scope = MongoField("scope")
    scope_value = MongoField("scope_value")
    amazon_attribute = MongoField("amazon_attribute")
    rule_type = MongoField("rule_type")
    rule_value = MongoField("rule_value")
    updated_at = MongoField("updated_at")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "updated_at"):
            self.updated_at = datetime.datetime.utcnow()

class GenerationTask(ModelBase):
    __tablename__ = "generation_tasks"
    
    id = MongoField("id")
    skus_input = MongoField("skus_input")
    status = MongoField("status")
    progress = MongoField("progress")
    log_messages = MongoField("log_messages")
    validation_report = MongoField("validation_report")
    output_file_path = MongoField("output_file_path")
    created_at = MongoField("created_at")
    completed_at = MongoField("completed_at")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "id"):
            self.id = str(uuid.uuid4())
        if not hasattr(self, "status"):
            self.status = "pending"
        if not hasattr(self, "progress"):
            self.progress = 0
        if not hasattr(self, "log_messages"):
            self.log_messages = ""
        if not hasattr(self, "validation_report"):
            self.validation_report = "{}"
        if not hasattr(self, "created_at"):
            self.created_at = datetime.datetime.utcnow()
