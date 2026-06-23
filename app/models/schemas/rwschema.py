from app.models.domain.rwmodel import RWModel


class RWSchema(RWModel):
    class Config(RWModel.Config):
        from_attributes = True
