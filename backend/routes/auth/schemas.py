from pydantic import BaseModel, field_validator

class RegisterRequest(BaseModel):
	username: str
	password: str

	@field_validator("username")
	@classmethod
	def username_must_be_valid(cls, v: str) -> str:
		v = v.strip()
		if len(v) < 3 or len(v) > 64:
			raise ValueError("Username must be between 3 and 64 characters")
		return v

	@field_validator("password")
	@classmethod
	def password_must_be_valid(cls, v: str) -> str:
		if len(v) < 8 or len(v) > 128:
			raise ValueError("Password must be between 8 and 128 characters")
		return v


class LoginRequest(BaseModel):
	username: str
	password: str