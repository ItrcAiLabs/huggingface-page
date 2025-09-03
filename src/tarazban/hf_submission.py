import os, uuid, json
from datetime import datetime
import pytz
import pandas as pd
from datasets import load_dataset, Dataset
from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError


HF_TOKEN = os.environ.get("HF_TOKEN")
DATASET_NAME = "ailabs-itrc/requests"   # یا your-username/requests

def ensure_private_dataset(repo_id: str, token: str):
    """
    اگر دیتاست وجود نداشته باشد، آن را به صورت Private می‌سازد.
    اگر وجود دارد، کاری نمی‌کند.
    """
    api = HfApi(token=token)
    try:
        # اگر نبود، بساز
        api.create_repo(
            repo_id=repo_id,          # مثال: "ailabs-itrc/requests"
            repo_type="dataset",
            private=True,             # مهم: پرایوت
            exist_ok=True
        )
    except HfHubHTTPError as e:
        # اگر 403 گرفتی یعنی توکن دسترسی ساخت زیر org را ندارد
        raise RuntimeError(
            f"Cannot create dataset '{repo_id}'. "
            f"Check Org Write permission for this token. Original: {e}"
        )

def submit_request(
    model_name, revision, precision, weight_type,
    model_type, params, license_str, private_bool
):
    TRIM_CHARS = ' \t\n\r"\'`.,:;!؟،؛…«»()[]{}|/\\'
    
    model_name = model_name.strip(TRIM_CHARS)
    try:
        # if not HF_TOKEN:
        #     return "❌ Error: Secret HF_TOKEN not found in Space."

        # # 1) مطمئن شو دیتاست وجود دارد (و پرایوت است)
        # ensure_private_dataset(DATASET_NAME, HF_TOKEN)
        api = HfApi(token=HF_TOKEN)

#         # 🔍 اول: چک کن مدل روی Hub وجود داره یا نه
        try:
            api.model_info(model_name)  # اگر نبود، خطا میده
        except HfHubHTTPError as e:
            code = e.response.status_code if getattr(e, "response", None) else "?"
            # if code == 404:
            return f"❌ Error: Model '{model_name}' not found on Hugging Face Hub."
            # return f"❌ Error while checking model on Hub: {e}"
        # 2) دیتاست را بخوان (اگر خالی بود، از لیست خالی شروع می‌کنیم)
        try:
            dataset = load_dataset(DATASET_NAME, split="train", token=HF_TOKEN)
        except Exception:
            dataset = Dataset.from_list([])  # دیتاست جدید/خالی

        # 3) چک تکراری نبودن
        existing_models = [entry.get("model") for entry in dataset]
        if model_name in existing_models:
            return f"⚠️ Model '{model_name}' already exists."

        # 4) رکورد جدید
        tehran = pytz.timezone("Asia/Tehran")
        now = datetime.now(tehran).strftime("%Y-%m-%dT%H:%M:%S")

        new_entry = {
            "id": str(uuid.uuid4()),
            "model": model_name,
            "revision": revision,
            "precision": precision,
            "weight_type": weight_type,
            "submitted_time": now,
            "model_type": model_type,
            "params": float(params) if (params not in [None, ""]) else None,
            "license": license_str,
            "private": bool(private_bool),
            "status": "⏳ pending"
        }

        dataset = dataset.add_item(new_entry)

        # 5) پوش به هاب
        dataset.push_to_hub(DATASET_NAME, token=HF_TOKEN)

        return f"✅ Submitted! ID: {new_entry['id']}"
    except HfHubHTTPError as e:
        # خطاهای هاب را خواناتر کن
        return (
            "❌ Error while pushing to Hub:\n"
            f"{e}\n\n"
            "راهنما: اگر 403 می‌بینی، توکن باید Org Write برای 'ailabs-itrc' داشته باشد "
            "یا DATASET_NAME را موقتاً به فضای شخصی خودت ببری."
        )
    except Exception as e:
        return f"❌ Error: {e}"
