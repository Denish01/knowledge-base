"""
Design Generator
Creates AI-generated designs optimized for POD products.

Supports multiple providers with automatic fallback:
1. DALL-E 3 (OpenAI) - Best quality
2. Ideogram - Best for text in images
3. Leonardo.ai - Good free tier
4. Replicate (Flux/SDXL) - Flexible
"""

import os
import json
import time
import random
import base64
import requests
from io import BytesIO
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow not installed. Run: pip install Pillow")

from config import (
    OPENAI_API_KEY, IDEOGRAM_API_KEY, REPLICATE_API_KEY,
    DESIGN_TEMPLATES, IMAGE_SIZE, UPSCALE_TO, MIN_QUALITY_SCORE
)

# Optional Google API key
try:
    from config import GOOGLE_API_KEY
except ImportError:
    GOOGLE_API_KEY = ""
from trend_scanner import get_quote_ideas

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "generated_designs"
OUTPUT_DIR.mkdir(exist_ok=True)


def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "[i]", "SUCCESS": "[+]", "ERROR": "[!]", "WARN": "[*]"}.get(level, "")
    print(f"[{timestamp}] {prefix} {message}")


class DesignGenerator:
    """Multi-provider AI image generator with automatic fallback."""

    def __init__(self):
        self.providers = []

        # Initialize available providers (ORDER MATTERS - free first!)

        # 1. GOOGLE GEMINI (Imagen 3) - Free tier available
        if GOOGLE_API_KEY:
            self.providers.append(('gemini', self._generate_gemini))
            log("Google Gemini (Imagen 3) available (FREE tier)", "SUCCESS")

        # 2. STABLE HORDE - Volunteer network, 100% FREE, most reliable
        self.providers.append(('stablehorde', self._generate_stablehorde))
        log("Stable Horde available (FREE - volunteer network)", "SUCCESS")

        # 3. POLLINATIONS - 100% FREE, no API key needed
        self.providers.append(('pollinations', self._generate_pollinations))
        log("Pollinations.ai available (FREE)", "SUCCESS")

        # 3. PRODIA - Free Stable Diffusion API
        self.providers.append(('prodia', self._generate_prodia))
        log("Prodia available (FREE)", "SUCCESS")

        # 4. HUGGINGFACE - Free inference API (multiple model fallbacks)
        self.providers.append(('huggingface', self._generate_huggingface))
        log("HuggingFace available (FREE)", "SUCCESS")

        # 4. Replicate - Pay per use but cheap
        if REPLICATE_API_KEY:
            self.providers.append(('replicate', self._generate_replicate))
            log("Replicate (Flux) available", "SUCCESS")

        # 5. Ideogram - PAID FALLBACK ONLY
        if IDEOGRAM_API_KEY:
            self.providers.append(('ideogram', self._generate_ideogram))
            log("Ideogram available (PAID - fallback only)", "WARN")

        # 6. OpenAI - Most expensive, last resort
        if OPENAI_API_KEY:
            self.providers.append(('openai', self._generate_dalle))
            log("OpenAI (DALL-E 3) available (PAID - fallback only)", "WARN")

        if not self.providers:
            log("WARNING: No AI providers configured!", "ERROR")

    def generate(self, prompt, output_name, prefer_provider=None, aspect_ratio="1:1", resolution="2K"):
        """
        Generate an image with automatic fallback between providers.

        Args:
            prompt: The design prompt
            output_name: Base name for output file
            prefer_provider: Optional preferred provider name
            aspect_ratio: Image aspect ratio (1:1, 16:9, etc.)
            resolution: Image resolution (1K, 2K, 4K)

        Returns:
            dict with image_path, provider, metadata or None on failure
        """
        # Reorder providers if preference given
        providers = list(self.providers)
        if prefer_provider:
            providers.sort(key=lambda x: x[0] != prefer_provider)

        for provider_name, generate_func in providers:
            try:
                log(f"Generating with {provider_name}...")

                # Pass aspect_ratio to Gemini, others use default square
                if provider_name == 'gemini':
                    result = generate_func(prompt, output_name, aspect_ratio=aspect_ratio, resolution=resolution)
                else:
                    result = generate_func(prompt, output_name)

                if result and result.get('image_path'):
                    result['provider'] = provider_name
                    log(f"Generated: {result['image_path']}", "SUCCESS")
                    return result

            except Exception as e:
                log(f"{provider_name} failed: {str(e)[:50]}", "WARN")
                continue

        log("All providers failed!", "ERROR")
        return None

    def _generate_gemini(self, prompt, output_name, aspect_ratio="1:1", resolution="2K"):
        """
        Generate image using Google Gemini with proper SDK.
        Supports different aspect ratios and resolutions.
        Free tier available via Google AI Studio.
        """
        try:
            from google import genai
            from google.genai import types

            # Initialize client
            client = genai.Client(api_key=GOOGLE_API_KEY)

            # Generate image
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=f"Create an image: {prompt}",
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=resolution
                    ),
                )
            )

            # Extract image from response
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data

                    output_path = OUTPUT_DIR / f"{output_name}_gemini.png"
                    with open(output_path, 'wb') as f:
                        f.write(image_data)

                    return {
                        'image_path': str(output_path),
                        'size': f"{resolution} {aspect_ratio}",
                        'cost': 0.00,
                    }

            raise Exception("No image in response")

        except ImportError:
            raise Exception("google-genai package not installed")
        except Exception as e:
            raise Exception(f"Gemini: {str(e)[:50]}")

    def _generate_stablehorde(self, prompt, output_name):
        """
        Generate image using Stable Horde - volunteer distributed network.
        100% FREE, no API key required (anonymous access).
        https://stablehorde.net/
        """
        # Anonymous API key
        api_key = "0000000000"

        # Request generation
        generate_url = "https://stablehorde.net/api/v2/generate/async"

        headers = {
            "apikey": api_key,
            "Content-Type": "application/json",
        }

        # Use simpler payload that works with anonymous access
        payload = {
            "prompt": prompt,
            "params": {
                "width": 512,
                "height": 512,
                "steps": 25,
                "cfg_scale": 7,
                "sampler_name": "k_euler",
            },
            "nsfw": False,
            "censor_nsfw": True,
            "models": ["stable_diffusion"],
            "r2": True,
        }

        try:
            response = requests.post(generate_url, headers=headers, json=payload, timeout=30)

            if response.status_code != 202:
                raise Exception(f"Request failed: {response.status_code}")

            data = response.json()
            request_id = data.get('id')

            if not request_id:
                raise Exception("No request ID returned")

            log(f"Stable Horde job queued: {request_id[:8]}...")

            # Poll for completion (volunteer network can take a while)
            check_url = f"https://stablehorde.net/api/v2/generate/check/{request_id}"
            status_url = f"https://stablehorde.net/api/v2/generate/status/{request_id}"

            for attempt in range(90):  # Up to 3 minutes
                time.sleep(2)

                check_response = requests.get(check_url, headers=headers, timeout=30)
                check_data = check_response.json()

                if check_data.get('done'):
                    # Get the result
                    status_response = requests.get(status_url, headers=headers, timeout=30)
                    status_data = status_response.json()

                    generations = status_data.get('generations', [])
                    if generations:
                        img_url = generations[0].get('img')

                        if img_url:
                            # Download the image
                            img_response = requests.get(img_url, timeout=60)

                            if img_response.status_code == 200 and len(img_response.content) > 5000:
                                output_path = OUTPUT_DIR / f"{output_name}_horde.png"
                                with open(output_path, 'wb') as f:
                                    f.write(img_response.content)

                                return {
                                    'image_path': str(output_path),
                                    'size': "1024x1024",
                                    'cost': 0.00,
                                }

                    raise Exception("No image in response")

                # Show queue position occasionally
                if attempt % 10 == 0:
                    queue_pos = check_data.get('queue_position', '?')
                    log(f"  Queue position: {queue_pos}")

            raise Exception("Generation timed out (3 min)")

        except Exception as e:
            raise Exception(f"Stable Horde: {e}")

    def _generate_pollinations(self, prompt, output_name):
        """
        Generate image using Pollinations.ai - 100% FREE, no API key needed!
        Uses Flux model under the hood.
        """
        import urllib.parse

        # Simplify prompt for URL (remove special chars)
        simple_prompt = prompt.replace('"', '').replace("'", "")
        encoded_prompt = urllib.parse.quote(simple_prompt, safe='')

        # Try multiple Pollinations endpoints
        endpoints = [
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={random.randint(1,999999)}&nologo=true&model=flux",
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={random.randint(1,999999)}&nologo=true",
        ]

        for url in endpoints:
            try:
                response = requests.get(url, timeout=180, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })

                # Check for valid PNG (magic bytes) or JPEG
                is_png = response.content[:8] == b'\x89PNG\r\n\x1a\n'
                is_jpeg = response.content[:2] == b'\xff\xd8'

                if (response.status_code == 200 and
                    len(response.content) > 10000 and
                    (is_png or is_jpeg)):

                    ext = "png" if is_png else "jpg"
                    output_path = OUTPUT_DIR / f"{output_name}_pollinations.{ext}"
                    with open(output_path, 'wb') as f:
                        f.write(response.content)

                    return {
                        'image_path': str(output_path),
                        'size': "1024x1024",
                        'cost': 0.00,
                    }

            except Exception:
                continue

        raise Exception(f"All Pollinations endpoints failed")

    def _generate_huggingface(self, prompt, output_name):
        """
        Generate image using HuggingFace free inference API.
        Tries multiple models for reliability.
        """
        # Models to try (in order of preference)
        models = [
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5",
            "CompVis/stable-diffusion-v1-4",
        ]

        headers = {
            "Content-Type": "application/json",
        }

        for model in models:
            url = f"https://api-inference.huggingface.co/models/{model}"

            payload = {
                "inputs": prompt,
            }

            try:
                log(f"  Trying HuggingFace model: {model.split('/')[-1]}")
                response = requests.post(url, headers=headers, json=payload, timeout=120)

                # Handle model loading (503)
                if response.status_code == 503:
                    log("  Model loading, waiting 20s...")
                    time.sleep(20)
                    response = requests.post(url, headers=headers, json=payload, timeout=120)

                if response.status_code == 200 and len(response.content) > 5000:
                    # Verify it's actually an image
                    is_png = response.content[:8] == b'\x89PNG\r\n\x1a\n'
                    is_jpeg = response.content[:2] == b'\xff\xd8'

                    if is_png or is_jpeg:
                        ext = "png" if is_png else "jpg"
                        output_path = OUTPUT_DIR / f"{output_name}_hf.{ext}"
                        with open(output_path, 'wb') as f:
                            f.write(response.content)

                        return {
                            'image_path': str(output_path),
                            'size': "1024x1024" if "xl" in model else "512x512",
                            'cost': 0.00,
                            'model': model,
                        }

            except Exception as e:
                log(f"  {model.split('/')[-1]} failed: {str(e)[:30]}")
                continue

        raise Exception("All HuggingFace models failed")

    def _generate_prodia(self, prompt, output_name):
        """
        Generate image using Prodia - FREE Stable Diffusion API.
        https://prodia.com/ - No API key required for basic usage.
        """
        # Prodia free API endpoint
        generate_url = "https://api.prodia.com/v1/sd/generate"

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "model": "v1-5-pruned-emaonly.safetensors [d7049739]",
            "prompt": prompt + ", high quality, professional design",
            "negative_prompt": "blurry, low quality, distorted, watermark, signature",
            "steps": 25,
            "cfg_scale": 7,
            "seed": random.randint(1, 999999999),
            "sampler": "DPM++ 2M Karras",
            "width": 512,
            "height": 512,
        }

        try:
            response = requests.post(generate_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                job_id = data.get('job')

                if job_id:
                    # Poll for result
                    status_url = f"https://api.prodia.com/v1/job/{job_id}"

                    for _ in range(60):  # Up to 2 minutes
                        time.sleep(2)
                        status_response = requests.get(status_url, timeout=30)

                        if status_response.status_code == 200:
                            status_data = status_response.json()

                            if status_data.get('status') == 'succeeded':
                                image_url = status_data.get('imageUrl')

                                if image_url:
                                    img_response = requests.get(image_url, timeout=60)

                                    if img_response.status_code == 200 and len(img_response.content) > 5000:
                                        output_path = OUTPUT_DIR / f"{output_name}_prodia.png"
                                        with open(output_path, 'wb') as f:
                                            f.write(img_response.content)

                                        return {
                                            'image_path': str(output_path),
                                            'size': "512x512",
                                            'cost': 0.00,
                                        }

                            elif status_data.get('status') == 'failed':
                                raise Exception("Job failed")

                    raise Exception("Timeout waiting for job")

            raise Exception(f"HTTP {response.status_code}")

        except Exception as e:
            raise Exception(f"Prodia: {e}")

    def _generate_dalle(self, prompt, output_name):
        """Generate image using OpenAI DALL-E 3."""
        url = "https://api.openai.com/v1/images/generations"

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        # Optimize prompt for DALL-E
        optimized_prompt = f"{prompt}, high quality, professional design, clean composition"

        payload = {
            "model": "dall-e-3",
            "prompt": optimized_prompt,
            "n": 1,
            "size": IMAGE_SIZE,
            "quality": "hd",
            "response_format": "b64_json"
        }

        response = requests.post(url, headers=headers, json=payload, timeout=120)
        data = response.json()

        if 'error' in data:
            raise Exception(data['error'].get('message', 'Unknown error'))

        # Decode and save image
        image_data = base64.b64decode(data['data'][0]['b64_json'])
        output_path = OUTPUT_DIR / f"{output_name}_dalle.png"

        with open(output_path, 'wb') as f:
            f.write(image_data)

        return {
            'image_path': str(output_path),
            'revised_prompt': data['data'][0].get('revised_prompt', prompt),
            'size': IMAGE_SIZE,
        }

    def _generate_ideogram(self, prompt, output_name):
        """Generate image using Ideogram API (best for text)."""
        url = "https://api.ideogram.ai/generate"

        headers = {
            "Api-Key": IDEOGRAM_API_KEY,
            "Content-Type": "application/json"
        }

        # Ideogram-specific optimizations
        payload = {
            "image_request": {
                "prompt": prompt,
                "aspect_ratio": "ASPECT_1_1",
                "model": "V_2",
                "magic_prompt_option": "AUTO",
                "style_type": "DESIGN"  # Optimized for merchandise
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=120)
        data = response.json()

        if 'data' not in data or not data['data']:
            raise Exception("No image generated")

        # Download the image
        image_url = data['data'][0]['url']
        image_response = requests.get(image_url, timeout=30)

        output_path = OUTPUT_DIR / f"{output_name}_ideogram.png"
        with open(output_path, 'wb') as f:
            f.write(image_response.content)

        return {
            'image_path': str(output_path),
            'size': "1024x1024",
        }

    def _generate_replicate(self, prompt, output_name):
        """Generate image using Replicate (Flux model)."""
        url = "https://api.replicate.com/v1/predictions"

        headers = {
            "Authorization": f"Token {REPLICATE_API_KEY}",
            "Content-Type": "application/json"
        }

        # Use Flux Schnell for speed
        payload = {
            "version": "black-forest-labs/flux-schnell",
            "input": {
                "prompt": prompt,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "png",
                "output_quality": 90,
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()

        if 'id' not in data:
            raise Exception("Failed to create prediction")

        prediction_id = data['id']

        # Poll for completion
        status_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"

        for _ in range(60):  # 60 attempts
            time.sleep(2)
            status_response = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_response.json()

            if status_data.get('status') == 'succeeded':
                output_urls = status_data.get('output', [])
                if output_urls:
                    image_response = requests.get(output_urls[0], timeout=30)

                    output_path = OUTPUT_DIR / f"{output_name}_flux.png"
                    with open(output_path, 'wb') as f:
                        f.write(image_response.content)

                    return {
                        'image_path': str(output_path),
                        'size': "1024x1024",
                    }

            elif status_data.get('status') == 'failed':
                raise Exception(status_data.get('error', 'Generation failed'))

        raise Exception("Generation timed out")


def build_prompt(idea):
    """
    Build a complete prompt from a design idea.

    Args:
        idea: Design idea dict from trend_scanner

    Returns:
        Optimized prompt string
    """
    template_name = idea.get('template', 'typography')
    template = DESIGN_TEMPLATES.get(template_name, DESIGN_TEMPLATES['typography'])

    prompt_vars = idea.get('prompt_vars', {})

    # Handle MICRO-NICHE typography designs (already have specific quotes)
    if template_name == 'typography':
        # Micro-niche ideas come with pre-made quotes
        if 'quote' not in prompt_vars:
            niche = idea.get('niche', 'motivation')
            sub_niche = idea.get('sub_niche', 'success')
            quotes = get_quote_ideas(niche, sub_niche, count=1)
            prompt_vars['quote'] = quotes[0] if quotes else f"I love {sub_niche}"

        # Set default style
        if 'style' not in prompt_vars:
            prompt_vars['style'] = random.choice(['bold modern', 'vintage retro', 'hand-lettered', 'minimalist'])

        # Set color scheme
        if 'color_scheme' not in prompt_vars:
            prompt_vars['color_scheme'] = random.choice(['black and white', 'vibrant', 'pastel', 'earth tones'])

    # Handle illustration designs
    elif template_name == 'illustration':
        if 'mood' not in prompt_vars:
            prompt_vars['mood'] = random.choice(['happy', 'peaceful', 'energetic', 'cozy'])

        if 'color_scheme' not in prompt_vars:
            prompt_vars['color_scheme'] = random.choice(['warm', 'cool', 'vibrant', 'muted'])

    # Handle vintage badge designs
    elif template_name == 'vintage_badge':
        if 'decade' not in prompt_vars:
            prompt_vars['decade'] = random.choice(['70', '80', '90'])

        if 'color_scheme' not in prompt_vars:
            prompt_vars['color_scheme'] = random.choice(['worn', 'faded', 'classic', 'distressed'])

    # Handle minimalist designs
    elif template_name == 'minimalist':
        if 'color' not in prompt_vars:
            prompt_vars['color'] = random.choice(['black', 'white', 'navy blue', 'forest green'])

    # Handle retro sunset designs
    elif template_name == 'retro_sunset':
        pass  # Template is self-contained

    # Handle educational infographic designs
    elif template_name == 'infographic':
        # Educational content comes with title and content pre-set
        if 'title' not in prompt_vars:
            prompt_vars['title'] = idea.get('subject', 'Educational Chart')
        if 'content' not in prompt_vars:
            prompt_vars['content'] = f"Educational diagram about {idea.get('subject', 'topic')}"
        if 'style' not in prompt_vars:
            prompt_vars['style'] = 'child-friendly, colorful, educational'
        if 'color_scheme' not in prompt_vars:
            prompt_vars['color_scheme'] = 'bright primary colors'

    # Build the prompt
    try:
        prompt_template = template['prompt_template']
        prompt = prompt_template.format(**prompt_vars)
    except KeyError as e:
        log(f"Missing prompt variable: {e}", "WARN")
        # Fallback to a generic prompt
        subject = prompt_vars.get('subject', idea.get('sub_niche', 'design'))
        prompt = f"Modern design featuring {subject}, clean composition, suitable for merchandise, transparent background"

    # Add universal quality modifiers
    prompt += ", high quality, professional, print-ready, 300 DPI"

    return prompt


def generate_design_from_idea(generator, idea, index=0):
    """
    Generate a design from an idea dict.

    Args:
        generator: DesignGenerator instance
        idea: Design idea from trend_scanner
        index: Design index for naming

    Returns:
        Result dict or None
    """
    prompt = build_prompt(idea)

    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    idea_type = idea.get('type', 'custom')
    template = idea.get('template', 'design')

    output_name = f"{timestamp}_{idea_type}_{template}_{index}"

    log(f"Prompt: {prompt[:80]}...")

    # Set aspect ratio based on template type
    if template == 'infographic':
        aspect_ratio = "16:9"  # Better for educational posters
        resolution = "2K"
    else:
        aspect_ratio = "1:1"   # Square for t-shirts/POD
        resolution = "2K"

    # Use default provider order (free first, paid as fallback)
    result = generator.generate(prompt, output_name, prefer_provider=None,
                                aspect_ratio=aspect_ratio, resolution=resolution)

    if result:
        # Add metadata
        result['idea'] = idea
        result['prompt'] = prompt
        result['timestamp'] = timestamp

        # Save metadata alongside image
        metadata_path = Path(result['image_path']).with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

    return result


def upscale_image(image_path, target_size=None):
    """
    Upscale an image for print quality.

    Args:
        image_path: Path to source image
        target_size: Target size string like "4096x4096"

    Returns:
        Path to upscaled image
    """
    if not PIL_AVAILABLE:
        return image_path

    if target_size is None:
        target_size = UPSCALE_TO

    try:
        width, height = map(int, target_size.split('x'))

        img = Image.open(image_path)
        img_upscaled = img.resize((width, height), Image.Resampling.LANCZOS)

        # Save with _upscaled suffix
        output_path = Path(image_path).with_stem(Path(image_path).stem + "_upscaled")
        img_upscaled.save(output_path, "PNG", optimize=True)

        log(f"Upscaled to {target_size}: {output_path}", "SUCCESS")
        return str(output_path)

    except Exception as e:
        log(f"Upscale failed: {e}", "WARN")
        return image_path


def remove_background(image_path):
    """
    Remove background from image (for t-shirt designs).
    Uses rembg if available, otherwise returns original.
    """
    try:
        from rembg import remove

        img = Image.open(image_path)
        img_no_bg = remove(img)

        output_path = Path(image_path).with_stem(Path(image_path).stem + "_nobg")
        img_no_bg.save(output_path, "PNG")

        log(f"Background removed: {output_path}", "SUCCESS")
        return str(output_path)

    except ImportError:
        log("rembg not installed, skipping background removal", "WARN")
        return image_path
    except Exception as e:
        log(f"Background removal failed: {e}", "WARN")
        return image_path


if __name__ == "__main__":
    # Test the design generator
    print("=" * 60)
    print("DESIGN GENERATOR TEST")
    print("=" * 60)

    generator = DesignGenerator()

    # Test idea
    test_idea = {
        'type': 'test',
        'template': 'typography',
        'niche': 'pets',
        'sub_niche': 'dogs',
        'prompt_vars': {
            'style': 'bold modern',
            'color_scheme': 'black and white',
        }
    }

    if generator.providers:
        result = generate_design_from_idea(generator, test_idea, index=0)
        if result:
            print(f"\nGenerated: {result['image_path']}")
            print(f"Provider: {result['provider']}")
    else:
        print("\nNo API providers configured. Add keys to config.py")
