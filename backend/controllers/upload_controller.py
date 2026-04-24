from flask import current_app, jsonify, request

from ai_engine.pipeline import AIPipeline
from database.db import get_store
from services.aggregator_service import AggregatorService
from services.api_service import APIService
from services.file_service import FileService
from services.processing_service import ProcessingService
from services.scraper_service import ScraperService


def upload_data():
    payload = request.get_json(silent=True) if request.is_json else {}
    raw_text = request.form.get("text") or payload.get("text")
    uploaded_file = request.files.get("file")

    if not raw_text and not uploaded_file:
        return jsonify({"error": "Provide text input or upload a supported file."}), 400

    file_service = FileService(current_app.config["UPLOAD_FOLDER"])
    extracted_text = ""
    file_name = None

    if uploaded_file:
        saved_path = file_service.save_upload(uploaded_file)
        extracted_text = file_service.extract_text(saved_path)
        file_name = saved_path.name
        file_entry = {
            **file_service.describe_source(saved_path),
            "text": ProcessingService.clean_text(extracted_text)
            or f"Uploaded {saved_path.suffix.lstrip('.').upper()} report: {saved_path.name}",
        }
    elif raw_text:
        extracted_text = raw_text
        file_entry = None
    else:
        file_entry = None

    clean_text = ProcessingService.clean_text(extracted_text)
    normalized_entries = AggregatorService.collect_entries(
        manual_text=ProcessingService.clean_text(raw_text) if raw_text else None,
        file_entry=file_entry,
    )

    results = _process_entries(normalized_entries, file_name=file_name)
    return jsonify({"result": results[0], "results": results}), 201


def sync_external_sources():
    normalized_entries = AggregatorService.collect_entries(
        api_entries=APIService.fetch_external_data(),
        scraped_entries=ScraperService.fetch_news_signals(),
    )
    results = _process_entries(normalized_entries)
    return jsonify({"results": results, "sources_processed": len(normalized_entries)}), 200


def _process_entries(normalized_entries, file_name=None):
    pipeline = AIPipeline()
    processed_results = []
    store = get_store()

    for entry in normalized_entries:
        pipeline_result = pipeline.run(entry)
        response_payload = {
            **pipeline_result,
            "clean_extracted_text": entry["text"],
            "file_name": file_name,
        }
        store.create_case(response_payload)
        processed_results.append(response_payload)

    return processed_results
