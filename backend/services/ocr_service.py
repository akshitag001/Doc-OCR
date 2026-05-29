import logging
import os
import uuid
from pathlib import Path
from typing import Dict, List, Union, Optional, Any
import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_UPLOADS_DIR = Path("uploads")

def _uploads_dir() -> Path:
    return Path(os.getenv("UPLOADS_DIR", str(DEFAULT_UPLOADS_DIR)))

def _thumbs_dir() -> Path:
    return _uploads_dir() / "thumbs"


class OCRService:
    """Handle OCR operations using EasyOCR/Tesseract with preprocessing."""
    
    def __init__(self):
        self.easyocr_reader = None
        self.easyocr_initialized = False
    
    def preprocess_image(self, file_path: str) -> Union[str, List[str]]:
        """
        Preprocess image for better OCR results.
        Returns path to processed image(s). For PDFs, returns list of page paths.
        """
        logger.info(f"[OCR] Starting preprocessing: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        
        # Handle PDF
        if file_ext == ".pdf":
            return self._preprocess_pdf(file_path)
        
        # Handle image
        return self._preprocess_image_file(file_path)
    
    def _preprocess_pdf(self, file_path: str) -> List[str]:
        """Convert PDF to preprocessed images, return list of paths."""
        try:
            from pdf2image import convert_from_path
        except ImportError:
            logger.error("[OCR] pdf2image not installed")
            raise
        
        logger.info(f"[OCR] Converting PDF: {file_path}")
        
        try:
            pages = convert_from_path(file_path, dpi=300)
            logger.info(f"[OCR] PDF has {len(pages)} pages")
            
            processed_paths = []
            _uploads_dir().mkdir(parents=True, exist_ok=True)
            for page_num, page_image in enumerate(pages, start=1):
                # Convert PIL Image to numpy array (BGR)
                img_array = np.array(page_image)
                # PIL loads as RGB, convert to BGR for OpenCV
                import cv2
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Process and save
                processed_img = self._apply_preprocessing(img_bgr)
                output_path = _uploads_dir() / f"{uuid.uuid4()}_page_{page_num}.png"
                cv2.imwrite(str(output_path), processed_img)
                processed_paths.append(str(output_path))
                logger.info(f"[OCR] Saved PDF page {page_num} to {output_path}")
            
            return processed_paths
        
        except Exception as e:
            logger.error(f"[OCR] PDF preprocessing failed: {e}")
            raise
    
    def _preprocess_image_file(self, file_path: str) -> str:
        """Preprocess single image file."""
        import cv2
        
        logger.info(f"[OCR] Loading image: {file_path}")
        
        try:
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError(f"Failed to load image: {file_path}")
            
            # Apply preprocessing steps
            processed_img = self._apply_preprocessing(img)
            
            # Save processed image
            _uploads_dir().mkdir(parents=True, exist_ok=True)
            output_path = _uploads_dir() / f"{Path(file_path).stem}_processed.png"
            cv2.imwrite(str(output_path), processed_img)
            logger.info(f"[OCR] Saved preprocessed image to {output_path}")
            
            return str(output_path)
        
        except Exception as e:
            logger.error(f"[OCR] Image preprocessing failed: {e}")
            raise
    
    def _apply_preprocessing(self, img: np.ndarray) -> np.ndarray:
        """Apply all preprocessing steps to image."""
        import cv2
        
        # Step 1: Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        logger.info("[OCR] Converted to grayscale")
        
        # Step 2: Deskew
        deskewed = self._deskew_image(gray)
        logger.info("[OCR] Deskew applied")
        
        # Step 3: Denoise
        denoised = cv2.fastNlMeansDenoising(deskewed, None, h=10)
        logger.info("[OCR] Denoising applied")
        
        # Step 4: Adaptive threshold (if image looks like scanned document)
        img_std = cv2.calcHist([denoised], [0], None, [256], [0, 256]).std()
        if img_std < 60:
            thresholded = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            logger.info("[OCR] Adaptive threshold applied (scanned doc detected)")
        else:
            thresholded = denoised
        
        # Step 5: Upscale if too small
        height, width = thresholded.shape
        if width < 1000:
            scale = 1000 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            upscaled = cv2.resize(thresholded, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            logger.info(f"[OCR] Upscaled from {width}x{height} to {new_width}x{new_height}")
            return upscaled
        
        return thresholded
    
    def _deskew_image(self, img: np.ndarray) -> np.ndarray:
        """Detect and correct image skew."""
        import cv2
        
        # Threshold image
        _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours and get rotation angle using minAreaRect
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            logger.info("[OCR] No contours found, skipping deskew")
            return img
        
        # Get largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]
        
        # Normalize angle to [-90, 0]
        if angle < -45:
            angle = 90 + angle
        
        # Only rotate if angle is significant
        if abs(angle) > 0.5 and abs(angle) < 45:
            logger.info(f"[OCR] Skew angle detected: {angle:.2f}°")
            
            h, w = img.shape
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(img, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)
            return rotated
        
        return img
    
    def extract_text(self, image_path: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Extract text from image(s) using OCR.
        Returns dict with raw_text, blocks, page_results, overall_confidence.
        """
        logger.info(f"[OCR] Starting text extraction from: {image_path}")
        
        # Handle both single and multiple images
        image_paths = image_path if isinstance(image_path, list) else [image_path]
        
        all_raw_text = []
        all_blocks = []
        page_results = []
        all_confidences = []
        
        for page_num, img_path in enumerate(image_paths, start=1):
            logger.info(f"[OCR] Processing page {page_num}/{len(image_paths)}")
            
            # Extract text from this page
            page_text, blocks, confidence = self._extract_text_from_image(str(img_path))
            
            all_raw_text.append(page_text)
            all_blocks.extend(blocks)
            all_confidences.extend([b["confidence"] for b in blocks])
            
            page_results.append({
                "page": page_num,
                "text": page_text,
                "blocks": blocks
            })
        
        # Concatenate text with page separators
        raw_text = "\n--- Page 1 ---\n".join(all_raw_text) if len(all_raw_text) > 1 else (all_raw_text[0] if all_raw_text else "")
        
        # Calculate overall confidence
        overall_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
        
        logger.info(f"[OCR] Extraction complete. Overall confidence: {overall_confidence:.1f}%")
        
        return {
            "raw_text": raw_text,
            "blocks": all_blocks,
            "page_results": page_results,
            "overall_confidence": overall_confidence
        }
    
    def _extract_text_from_image(self, image_path: str) -> tuple:
        """Extract text from single image, return (text, blocks, confidence)."""
        import cv2
        from PIL import Image, ImageEnhance
        
        # Try EasyOCR first
        text, blocks, confidence = self._ocr_with_easyocr(image_path)
        word_count = len(text.split())
        
        logger.info(f"[OCR] EasyOCR result: {word_count} words, confidence {confidence:.1f}%")
        
        # Check if we should fallback
        if word_count < 10 or confidence < 50:
            logger.warning("[OCR] EasyOCR returned low confidence, trying Tesseract fallback")
            
            tess_text, tess_blocks, tess_confidence = self._ocr_with_tesseract(image_path)
            tess_word_count = len(tess_text.split())
            
            if tess_word_count > word_count:
                logger.info(f"[OCR] Tesseract better: {tess_word_count} words vs {word_count}")
                text, blocks, confidence = tess_text, tess_blocks, tess_confidence
                word_count = tess_word_count
        
        # If still low, try contrast enhancement
        if word_count < 5:
            logger.warning("[OCR] Low word count after both engines, trying contrast enhancement")
            
            try:
                img = Image.open(image_path)
                enhanced = ImageEnhance.Contrast(img).enhance(2.0)
                enhanced_path = Path(image_path).stem + "_enhanced.png"
                enhanced.save(enhanced_path)
                
                text, blocks, confidence = self._ocr_with_easyocr(enhanced_path)
                word_count = len(text.split())
                
                logger.info(f"[OCR] After contrast enhancement: {word_count} words")
            except Exception as e:
                logger.error(f"[OCR] Contrast enhancement failed: {e}")
        
        # Final check
        if word_count < 5:
            from models.exceptions import DocumentQualityError
            raise DocumentQualityError(
                "Unable to extract text. Please upload a higher quality scan."
            )
        
        return text, blocks, confidence
    
    def _ocr_with_easyocr(self, image_path: str) -> tuple:
        """Run EasyOCR on image, return (text, blocks, avg_confidence)."""
        try:
            import easyocr
        except ImportError:
            logger.error("[OCR] easyocr not installed")
            return "", [], 0.0
        
        try:
            # Initialize reader once
            if not self.easyocr_initialized:
                logger.info("[OCR] Initializing EasyOCR reader...")
                self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
                self.easyocr_initialized = True
            
            results = self.easyocr_reader.readtext(image_path, detail=1, paragraph=False)
            
            # Parse results
            text_parts = []
            blocks = []
            confidences = []
            
            for (bbox, text, conf) in results:
                if conf >= 0.3:  # Filter low confidence
                    text_parts.append(text)
                    confidences.append(conf * 100)
                    
                    # Convert bbox to [x, y, w, h]
                    bbox_array = np.array(bbox)
                    x_min, y_min = bbox_array.min(axis=0)
                    x_max, y_max = bbox_array.max(axis=0)
                    
                    blocks.append({
                        "text": text,
                        "confidence": conf * 100,
                        "bbox": [int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)]
                    })
            
            text = " ".join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return text, blocks, avg_confidence
        
        except Exception as e:
            logger.error(f"[OCR] EasyOCR failed: {e}")
            return "", [], 0.0
    
    def _ocr_with_tesseract(self, image_path: str) -> tuple:
        """Run Tesseract OCR on image, return (text, blocks, avg_confidence)."""
        try:
            import pytesseract
            from pytesseract import Output
            from PIL import Image
        except ImportError:
            logger.error("[OCR] pytesseract not installed")
            return "", [], 0.0
        
        try:
            img = Image.open(image_path)
            
            # Extract text with bounding boxes
            data = pytesseract.image_to_data(img, output_type=Output.DICT, config='--psm 3')
            
            text_parts = []
            blocks = []
            confidences = []
            
            for i, conf in enumerate(data['conf']):
                if int(conf) > 30:  # Filter low confidence
                    text = data['text'][i]
                    if text.strip():
                        text_parts.append(text)
                        confidences.append(int(conf))
                        
                        blocks.append({
                            "text": text,
                            "confidence": float(conf),
                            "bbox": [
                                data['left'][i],
                                data['top'][i],
                                data['width'][i],
                                data['height'][i]
                            ]
                        })
            
            text = " ".join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            logger.info(f"[OCR] Tesseract result: {len(text_parts)} items, confidence {avg_confidence:.1f}%")
            
            return text, blocks, avg_confidence
        
        except Exception as e:
            logger.error(f"[OCR] Tesseract failed: {e}")
            return "", [], 0.0
    
    def get_document_thumbnail(self, file_path: str, job_id: str) -> str:
        """
        Create thumbnail from document (first page for PDFs, whole image for images).
        Returns path to thumbnail.
        """
        logger.info(f"[OCR] Generating thumbnail for: {file_path}")
        
        _thumbs_dir().mkdir(parents=True, exist_ok=True)
        
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == ".pdf":
                thumbnail_path = self._thumbnail_from_pdf(file_path, job_id)
            else:
                thumbnail_path = self._thumbnail_from_image(file_path, job_id)
            
            logger.info(f"[OCR] Thumbnail saved to {thumbnail_path}")
            return thumbnail_path
        
        except Exception as e:
            logger.error(f"[OCR] Thumbnail generation failed: {e}")
            return ""
    
    def _thumbnail_from_pdf(self, file_path: str, job_id: str) -> str:
        """Extract first page of PDF as thumbnail."""
        try:
            from pdf2image import convert_from_path
        except ImportError:
            logger.error("[OCR] pdf2image not installed")
            raise
        
        try:
            pages = convert_from_path(file_path, dpi=150, first_page=1, last_page=1)
            if not pages:
                raise ValueError("PDF has no pages")
            
            page = pages[0]
            
            # Resize to max 400px wide
            max_width = 400
            if page.width > max_width:
                ratio = max_width / page.width
                new_height = int(page.height * ratio)
                page = page.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            thumb_path = _thumbs_dir() / f"{job_id}_thumb.png"
            page.save(thumb_path, "PNG")
            
            return str(thumb_path)
        
        except Exception as e:
            logger.error(f"[OCR] PDF thumbnail failed: {e}")
            raise
    
    def _thumbnail_from_image(self, file_path: str, job_id: str) -> str:
        """Create thumbnail from image."""
        try:
            from PIL import Image
        except ImportError:
            logger.error("[OCR] Pillow not installed")
            raise
        
        try:
            img = Image.open(file_path)
            
            # Resize to max 400px wide
            max_width = 400
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            thumb_path = _thumbs_dir() / f"{job_id}_thumb.png"
            img.save(thumb_path, "PNG")
            
            return str(thumb_path)
        
        except Exception as e:
            logger.error(f"[OCR] Image thumbnail failed: {e}")
            raise


