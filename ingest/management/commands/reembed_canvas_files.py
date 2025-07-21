from django.core.management.base import BaseCommand
from ingest.models import CanvasFile, CanvasChunk
from ingest.tasks import create_chunks_for_object, process_canvas_chunks


class Command(BaseCommand):
    help = "Re-embed any CanvasFile objects that don't already have CanvasChunks."

    def add_arguments(self, parser):
        parser.add_argument(
            "--async",
            action="store_true",
            help="Use Celery to process files asynchronously."
        )
        parser.add_argument(
            "--course-id",
            type=int,
            default=None,
            help="Optional course ID to limit re-embedding to a single course."
        )

    def handle(self, *args, **options):
        async_mode = options["async"]
        course_id = options["course_id"]

        # Filter CanvasFiles without chunks
        files_without_chunks = CanvasFile.objects.exclude(
            id__in=CanvasChunk.objects.filter(parent_type="file").values_list("parent_id", flat=True)
        )

        if course_id:
            files_without_chunks = files_without_chunks.filter(course_id=course_id)

        if not files_without_chunks.exists():
            self.stdout.write(self.style.SUCCESS("No CanvasFile objects require re-embedding."))
            return

        self.stdout.write(
            self.style.NOTICE(f"Found {files_without_chunks.count()} CanvasFile(s) requiring re-embedding.")
        )

        if async_mode:
            # Queue a single Celery task per course
            courses = files_without_chunks.values_list("course_id", flat=True).distinct()
            for cid in courses:
                self.stdout.write(f"Queueing re-embedding for course {cid}...")
                process_canvas_chunks.delay(course_id=cid)
            self.stdout.write(self.style.SUCCESS("All tasks have been queued."))
        else:
            # Process synchronously
            for f in files_without_chunks:
                self.stdout.write(f"Processing CanvasFile {f.id} ({f.filename})...")
                try:
                    create_chunks_for_object("file", f.id, f.text)
                    self.stdout.write(self.style.SUCCESS(f"  Successfully processed CanvasFile {f.id}."))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"  Failed for CanvasFile {f.id}: {e}"))
