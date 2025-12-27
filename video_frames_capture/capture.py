import typer
import cv2
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Typer App Initialization
app = typer.Typer(help="CLI tool to capture frames from a camera.")


@app.command()
def capture_frames(
        cam: int = typer.Option(
            0,
            "--cam", "-c",
            help="The index of the camera to capture from."),
        width_height: str = typer.Option(
            "640,360",
            "--wh",
            help="Resize capture frames to this width and height, in comma separated format,"
                 "e.g '1280,720'). Set as empty string or just '.' for no resizing"),
        interval: int = typer.Option(
            100,
            "--interval", "-i",
            help="Interval in milliseconds to wait between successive captures."
        ),
        output_dir: Path = typer.Option(Path("."), "--output-dir", "-o",
                                        help="Base directory to save the new frame directory."),
):
    """
    Captures frames from a camera and saves them to a new timestamped directory.
    Press 'q' to quit the application.
    """
    # Create a new directory for this session using a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = output_dir / f"frames_{timestamp}"
    os.makedirs(save_dir, exist_ok=True)
    typer.echo(f"📸 Saving frames to: {save_dir}")

    # Initialize the camera capture
    cap = cv2.VideoCapture(cam)
    if not cap.isOpened():
        typer.echo(f"❌ Error: Could not open camera with index {cam}.")
        raise typer.Exit(code=1)

    # Process width and height arguments
    target_wh = None
    if width_height not in ("", "."):
        try:
            width_str, height_str = width_height.split(',')
            target_wh = (int(width_str), int(height_str))
            typer.echo(f"📏 Resizing frames to {target_wh}.")
        except ValueError:
            typer.echo("❌ Invalid format for --wh. Please use 'width,height' (e.g., '1280,720').")
            raise typer.Exit(code=1)

    frame_count = 0
    frame = None  # will be populated in loop below if we are able to access camera
    last_frame_time = time.perf_counter() * 1000  # current time in milliseconds

    try:
        while True:
            # Check for elapsed time
            current_time = time.perf_counter() * 1000
            if (current_time - last_frame_time) >= interval:
                ret, frame = cap.read()
                if not ret:
                    typer.echo("❌ Failed to capture frame.")
                    break

                # Resize the frame if a new size was specified
                if target_wh:
                    frame = cv2.resize(frame, target_wh)

                # Save the frame
                frame_tstamp = datetime.now().strftime("%Y%m%d.%H%M%S.%f")[:-3]

                frame_path = save_dir / f"{frame_count:06d}.{frame_tstamp}.jpg"
                cv2.imwrite(frame_path, frame)
                typer.echo(f"🖼️ Saved frame: {frame_path.name} {frame.shape}")

                frame_count += 1
                last_frame_time = current_time

            # Display the live feed
            if frame is not None:
                cv2.imshow("Camera Feed (Press 'q' to quit)", frame)

            # Check for 'q' key press to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                typer.echo("👋 Quitting...")
                break

    finally:
        # Release the camera and close all windows
        cap.release()
        cv2.destroyAllWindows()
        typer.echo("✅ Capture complete.")


if __name__ == "__main__":
    app()