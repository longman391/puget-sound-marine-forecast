"""
Marine forecast scraper for fetching data from NOAA text files
"""

import httpx
import re
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ForecastPeriod:
    """Represents a single forecast period (e.g., TONIGHT, WED, etc.)"""
    name: str
    wind: str
    waves: str
    weather: Optional[str] = None


@dataclass
class MarineForecast:
    """Represents a complete marine forecast for a zone"""
    zone: str
    name: str
    issued: datetime
    expires: datetime
    periods: List[ForecastPeriod]


class ForecastScraper:
    """Scrapes and parses marine forecasts from NOAA text files"""
    
    BASE_URL = "https://tgftp.nws.noaa.gov/data/forecasts/marine/coastal/pz"
    
    async def fetch_zone_text(self, zone: str) -> str:
        """Fetch the raw text for a specific zone"""
        url = f"{self.BASE_URL}/{zone.lower()}.txt"
        
        # Configure timeout and retry settings for resilience
        timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                return response.text
            except httpx.TimeoutException:
                logger.error(f"Timeout fetching data for zone {zone}")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code} for zone {zone}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error fetching zone {zone}: {e}")
                raise
    
    def parse_forecast_text(self, text: str, zone: str) -> MarineForecast:
        """Parse the raw forecast text into structured data"""
        
        logger.info(f"Parsing forecast for zone {zone}")
        
        # Extract zone header information
        zone_match = re.search(rf'{zone.upper()}-(\d+)-\n(.+?)-\n(.+?)\n', text, re.IGNORECASE | re.MULTILINE)
        if not zone_match:
            logger.warning(f"Could not parse zone header for {zone}, using fallback")
            # Fallback: try to extract zone name from text
            name_match = re.search(rf'{zone.upper()}-\d+-\n(.+?)-', text, re.IGNORECASE)
            zone_name = name_match.group(1).strip() if name_match else f"Zone {zone.upper()}"
            expires_str = "999999"  # Default fallback
            issued_str = "Now"
        else:
            expires_str = zone_match.group(1)
            zone_name = zone_match.group(2).strip()
            issued_str = zone_match.group(3).strip()
        
        logger.info(f"Found zone: {zone_name}")
        
        # Parse timestamps
        issued = self._parse_timestamp(issued_str)
        expires = self._parse_expires(expires_str)
        
        # Extract forecast periods
        periods = self._extract_periods(text)
        
        logger.info(f"Extracted {len(periods)} forecast periods")
        
        return MarineForecast(
            zone=zone.upper(),
            name=zone_name,
            issued=issued,
            expires=expires,
            periods=periods
        )
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp from forecast text"""
        try:
            # Example: "305 PM PDT Tue Aug 5 2025"
            # More robust parsing would handle various formats
            from dateutil import parser
            
            # Clean up the timestamp string
            cleaned = timestamp_str.strip()
            
            # Try to parse with dateutil (handles many formats)
            try:
                return parser.parse(cleaned)
            except:
                # Fallback to current time if parsing fails
                return datetime.now()
                
        except:
            return datetime.now()
    
    def _parse_expires(self, expires_str: str) -> datetime:
        """Parse expiration timestamp from the header code"""
        try:
            # Example: "061115" means expires on 06th at 11:15
            if len(expires_str) == 6:
                day = int(expires_str[:2])
                hour = int(expires_str[2:4])
                minute = int(expires_str[4:6])
                
                # Assume current month/year for simplicity
                from datetime import datetime
                now = datetime.now()
                expires = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
                
                # If the day is in the past, assume next month
                if expires < now:
                    if expires.month == 12:
                        expires = expires.replace(year=expires.year + 1, month=1)
                    else:
                        expires = expires.replace(month=expires.month + 1)
                
                return expires
            else:
                # Fallback
                return datetime.now()
        except:
            return datetime.now()
    
    def _extract_periods(self, text: str) -> List[ForecastPeriod]:
        """Extract forecast periods from text"""
        periods = []
        
        # Find all periods starting with dots (e.g., .TONIGHT, .WED, etc.)
        period_pattern = r'\.([A-Z][A-Z\s]+?)\.\.\.(.+?)(?=\n\.|$$)'
        matches = re.findall(period_pattern, text, re.DOTALL | re.MULTILINE)
        
        for period_name, period_text in matches:
            period_name = period_name.strip()
            period_text = period_text.strip()
            
            # Extract wind information - more comprehensive pattern
            wind_patterns = [
                r'([NSEW]+\s+wind[^.]+?(?:kt|knots)[^.]*)',
                r'(Variable\s+wind[^.]+)',
                r'(Light\s+and\s+variable[^.]+)',
                r'(Calm[^.]*)'
            ]
            wind = ""
            for pattern in wind_patterns:
                wind_match = re.search(pattern, period_text, re.IGNORECASE)
                if wind_match:
                    wind = wind_match.group(1).strip()
                    break
            
            # Extract wave information - improved patterns with better boundaries
            wave_patterns = [
                # Most specific patterns first
                r'(Waves\s+around\s+[0-9]+\s+(?:ft|feet)\s+or\s+less)',
                r'(Waves\s+[0-9]+\s+to\s+[0-9]+\s+(?:ft|feet)(?:\s+or\s+less)?)',
                r'(Waves\s+around\s+[0-9]+\s+(?:ft|feet))',
                r'(Waves\s+[0-9]+\s+(?:ft|feet))',
                # More general patterns
                r'(Waves\s+around\s+[^.]+?(?:ft|feet)[^.]*?)(?=\s*[A-Z][a-z]|\s*[.!]|$)',
                r'(Waves\s+[^.]+?(?:ft|feet)[^.]*?)(?=\s*[A-Z][a-z]|\s*[.!]|$)',
                # Seas patterns
                r'(Seas\s+around\s+[0-9]+\s+(?:ft|feet)\s+or\s+less)',
                r'(Seas\s+[0-9]+\s+to\s+[0-9]+\s+(?:ft|feet)(?:\s+or\s+less)?)',
                r'(Seas\s+around\s+[0-9]+\s+(?:ft|feet))',
                r'(Seas\s+[0-9]+\s+(?:ft|feet))',
                r'(Seas\s+around\s+[^.]+?(?:ft|feet)[^.]*?)(?=\s*[A-Z][a-z]|\s*[.!]|$)',
                r'(Seas\s+[^.]+?(?:ft|feet)[^.]*?)(?=\s*[A-Z][a-z]|\s*[.!]|$)'
            ]
            waves = ""
            for pattern in wave_patterns:
                wave_match = re.search(pattern, period_text, re.IGNORECASE)
                if wave_match:
                    waves = wave_match.group(1).strip()
                    # Clean up common issues
                    waves = re.sub(r'\s+', ' ', waves)
                    # Make sure it ends properly
                    if not waves.endswith('.'):
                        waves = waves.rstrip('.,!') 
                    break
            
            # Extract weather conditions - everything else after removing wind/waves
            # Split by sentences and find weather-related content
            remaining_text = period_text
            if wind:
                remaining_text = remaining_text.replace(wind, '')
            if waves:
                remaining_text = remaining_text.replace(waves, '')
            
            # Clean up and extract weather
            weather_text = remaining_text.strip(' .,\n')
            
            # Remove any standalone "Waves" or "Seas" words that got left behind
            weather_text = re.sub(r'\b(Waves?|Seas?)\b\.?', '', weather_text, flags=re.IGNORECASE)
            weather_text = weather_text.strip(' .,\n')
            
            # Look for complete weather phrases and sentences
            weather_sentences = []
            
            # Split by periods and process each sentence
            sentences = re.split(r'[.]', weather_text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence or len(sentence) < 4:
                    continue
                
                # Skip sentences that are just wave details or technical info
                skip_patterns = [
                    r'^(Wave Detail|Combined seas)',
                    r'^\d+\s+ft\s+at\s+\d+\s+seconds',
                    r'^around\s+\d+\s+ft',
                    r'^\d+\s+to\s+\d+\s+ft'
                ]
                
                if any(re.match(pattern, sentence, re.IGNORECASE) for pattern in skip_patterns):
                    continue
                
                # Look for weather-related content
                weather_keywords = [
                    'shower', 'rain', 'storm', 'thunder', 'clear', 'sunny', 
                    'cloudy', 'overcast', 'fog', 'mist', 'chance', 'likely',
                    'possible', 'occasional', 'scattered', 'isolated', 'mainly',
                    'partly', 'mostly', 'becoming', 'then', 'until', 'after',
                    'tstms', 'thunderstorms'
                ]
                
                # Check if sentence contains weather keywords or looks like weather
                has_weather = any(keyword in sentence.lower() for keyword in weather_keywords)
                
                # Also include sentences that have typical weather sentence structure
                weather_patterns = [
                    r'\b(a|an)\s+(chance|slight\s+chance)\s+of\s+\w+',
                    r'\b(showers?|rain)\b',
                    r'\b(likely|possible|probable)\b',
                    r'\bmainly\s+in\s+the\s+(morning|afternoon|evening)\b'
                ]
                
                has_weather_pattern = any(re.search(pattern, sentence, re.IGNORECASE) for pattern in weather_patterns)
                
                if has_weather or has_weather_pattern:
                    # Clean up the sentence
                    sentence = re.sub(r'\s+', ' ', sentence).strip()
                    
                    # Fix common truncation issues by looking for context
                    if sentence.endswith(' of'):
                        # Try to find what comes after "of" in the original text
                        # Look for the pattern in context
                        of_pattern = rf'{re.escape(sentence[:-3])}\s+of\s+(\w+(?:\s+\w+)*)'
                        of_match = re.search(of_pattern, period_text, re.IGNORECASE)
                        if of_match:
                            sentence = sentence[:-3] + ' of ' + of_match.group(1)
                        else:
                            # Common weather completions
                            weather_completions = {
                                'a chance of': 'showers',
                                'a slight chance of': 'showers', 
                                'chance of': 'showers',
                                'possibility of': 'showers'
                            }
                            sentence_lower = sentence.lower()
                            for phrase, completion in weather_completions.items():
                                if sentence_lower.endswith(phrase):
                                    sentence = sentence + ' ' + completion
                                    break
                    
                    weather_sentences.append(sentence)
            
            # Join weather sentences
            if weather_sentences:
                weather = '. '.join(weather_sentences)
                # Final cleanup
                weather = re.sub(r'\s+', ' ', weather).strip()
                # Ensure proper capitalization
                if weather and not weather[0].isupper():
                    weather = weather[0].upper() + weather[1:]
            else:
                weather = None
            
            # Final check - don't put wave-only content in weather
            if weather and re.match(r'^(Waves?|Seas?)\b', weather, re.IGNORECASE):
                weather = None
            
            periods.append(ForecastPeriod(
                name=period_name,
                wind=wind,
                waves=waves,
                weather=weather
            ))
        
        return periods
    
    async def get_forecast(self, zone: str) -> MarineForecast:
        """Get complete forecast for a zone"""
        text = await self.fetch_zone_text(zone)
        return self.parse_forecast_text(text, zone)
