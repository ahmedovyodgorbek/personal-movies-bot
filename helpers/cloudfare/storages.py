from storages.backends.s3boto3 import S3Boto3Storage
from config import settings
import load_env


class PublicMediaStorage(S3Boto3Storage):
    """Used for article images (CKEditor)."""
    location = "telegram_bot" 
    base_url = f"{settings.CLOUDFLARE_R2_PUBLIC_URL}/telegram_bot"
    default_acl = "public-read"
    bucket_name = settings.CLOUDFLARE_R2_CONFIG_OPTIONS["bucket_name"]
    endpoint_url = settings.CLOUDFLARE_R2_CONFIG_OPTIONS["endpoint_url"]
    access_key = settings.CLOUDFLARE_R2_CONFIG_OPTIONS["access_key"]
    secret_key = settings.CLOUDFLARE_R2_CONFIG_OPTIONS["secret_key"]
    signature_version = settings.CLOUDFLARE_R2_CONFIG_OPTIONS["signature_version"]
    file_overwrite = False
    custom_domain = load_env.CUSTOM_DOMAIN
