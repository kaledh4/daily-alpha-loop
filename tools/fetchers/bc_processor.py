"""
Benjamin Cowen Methodology Processor
Refactored for integration with Unified Fetcher V3
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class CycleAnalysis:
    """Extracted cycle analysis from transcript"""
    video_id: str
    title: str
    upload_date: str
    timestamp: str
    
    # Core metrics mentioned
    btc_price: float = None
    eth_btc_ratio: float = None
    m2_yoy_growth: float = None
    fed_funds_rate: float = None
    roi_from_low: float = None
    days_since_peak: int = None
    
    # Qualitative assessments
    cycle_phase: str = ""
    fed_policy_stance: str = ""
    risk_level: str = ""
    
    # Pattern references
    historical_analogues: List[str] = None
    key_indicators_mentioned: List[str] = None
    
    # Extracted reasoning
    key_points: List[str] = None
    cycle_logic: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.historical_analogues is None: self.historical_analogues = []
        if self.key_indicators_mentioned is None: self.key_indicators_mentioned = []
        if self.key_points is None: self.key_points = []
        if self.cycle_logic is None: self.cycle_logic = []
        if self.warnings is None: self.warnings = []

class TranscriptProcessor:
    """Process Benjamin Cowen video transcripts"""
    
    PATTERNS = {
        'fed_policy': [r'federal reserve', r'fed pivot', r'rate cuts?', r'rate hikes?', r'quantitative (?:easing|tightening)', r'QE|QT', r'm2 (?:money supply|growth)'],
        'cycle_phase': [r'bull (?:market|run)', r'bear (?:market|run)', r'accumulation phase', r'euphori(?:a|c)', r'capitulation', r'mini bear'],
        'metrics': [r'eth[/]btc', r'total3[/]btc', r'bitcoin dominance', r'mvrv', r'roi from (?:low|bottom)', r'diminishing returns', r'logarithmic regression'],
        'historical': [r'2013 (?:cycle|top|bottom)', r'2017 (?:cycle|top|bottom)', r'2019 mini bear', r'2021 (?:cycle|top|bottom)', r'last cycle', r'previous (?:cycle|top|bottom)'],
        'risk_warnings': [r'be careful', r'manage (?:your )?risk', r'not (?:financial )?advice', r'zoom out', r'don\'t get caught up', r'extremely (?:overbought|oversold)']
    }
    
    def __init__(self, output_dir: str = "data"):
        self.output_dir = Path(output_dir)
        self.transcripts_dir = self.output_dir / "transcripts"
        self.indicators_dir = self.output_dir / "indicators"
        self.cycles_dir = self.output_dir / "cycles"
        
        # Create directories
        for d in [self.transcripts_dir, self.indicators_dir, self.cycles_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def extract_patterns(self, text: str, category: str) -> List[str]:
        matches = []
        text_lower = text.lower()
        for pattern in self.PATTERNS.get(category, []):
            if re.search(pattern, text_lower):
                matches.append(pattern.replace(r'\b', '').replace('?', ''))
        return list(set(matches))
    
    def extract_metrics(self, text: str) -> Dict[str, Any]:
        metrics = {}
        # Bitcoin price
        btc_match = re.search(r'bitcoin.{0,50}?(\$?[\d,]+\.?\d*)[k ]', text.lower())
        if btc_match:
            try:
                price_str = btc_match.group(1).replace(',', '').replace('$', '')
                price = float(price_str)
                if 'k' in btc_match.group(0): price *= 1000
                metrics['btc_price'] = price
            except ValueError: pass
        
        # ETH/BTC ratio
        eth_btc_match = re.search(r'eth[/]btc.{0,30}?(0\.\d+)', text.lower())
        if eth_btc_match:
            try: metrics['eth_btc_ratio'] = float(eth_btc_match.group(1))
            except ValueError: pass
            
        # M2 growth
        m2_match = re.search(r'm2.{0,30}?(-?\d+\.?\d*)%', text.lower())
        if m2_match:
            try: metrics['m2_yoy_growth'] = float(m2_match.group(1))
            except ValueError: pass
            
        # Fed funds rate
        ffr_match = re.search(r'federal funds rate.{0,30}?(\d+\.?\d*)%', text.lower())
        if ffr_match:
            try: metrics['fed_funds_rate'] = float(ffr_match.group(1))
            except ValueError: pass
            
        return metrics
    
    def extract_key_points(self, text: str) -> List[str]:
        sentences = re.split(r'[.!?]+', text)
        key_points = []
        importance_markers = ['important', 'key', 'critical', 'significant', 'historically', 'typically', 'usually', 'if we look at', 'what we see', 'what we\'re seeing', 'the question is', 'the point is', 'remember', 'keep in mind', 'don\'t forget']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20: continue
            sentence_lower = sentence.lower()
            if any(marker in sentence_lower for marker in importance_markers):
                key_points.append(sentence)
            elif re.search(r'\d+\.?\d*%|\$[\d,]+|ratio|index|level', sentence_lower):
                key_points.append(sentence)
        return key_points[:20]
    
    def assess_cycle_phase(self, text: str) -> str:
        text_lower = text.lower()
        phase_signals = {
            'accumulation': ['accumulation', 'bottom', 'capitulation', 'bear market bottom'],
            'bull_expansion': ['bull run', 'expansion', 'uptrend', 'rally'],
            'euphoria': ['euphoria', 'euphoric', 'top', 'peak', 'mania'],
            'bear': ['bear market', 'drawdown', 'correction', 'decline']
        }
        phase_scores = {phase: sum(1 for signal in signals if signal in text_lower) for phase, signals in phase_signals.items()}
        if max(phase_scores.values()) == 0: return "neutral"
        return max(phase_scores, key=phase_scores.get)
    
    def assess_risk_level(self, text: str) -> str:
        text_lower = text.lower()
        high_risk = ['overbought', 'extended', 'elevated risk', 'be careful', 'extreme', 'euphoria', 'top', 'caution']
        low_risk = ['oversold', 'compressed', 'bottom', 'accumulation', 'opportunity', 'undervalued']
        high_count = sum(1 for s in high_risk if s in text_lower)
        low_count = sum(1 for s in low_risk if s in text_lower)
        
        if high_count > low_count * 1.5: return "elevated"
        elif low_count > high_count * 1.5: return "compressed"
        else: return "neutral"

    def process_transcript(self, raw_text: str, video_id: str, title: str = "", upload_date: str = "") -> CycleAnalysis:
        analysis = CycleAnalysis(video_id=video_id, title=title, upload_date=upload_date, timestamp=datetime.utcnow().isoformat())
        
        metrics = self.extract_metrics(raw_text)
        for key, value in metrics.items(): setattr(analysis, key, value)
        
        analysis.historical_analogues = self.extract_patterns(raw_text, 'historical')
        analysis.key_indicators_mentioned = self.extract_patterns(raw_text, 'metrics')
        analysis.key_points = self.extract_key_points(raw_text)
        
        cycle_keywords = ['cycle', 'halving', 'bull', 'bear', 'top', 'bottom']
        analysis.cycle_logic = [p for p in analysis.key_points if any(kw in p.lower() for kw in cycle_keywords)]
        
        warning_keywords = ['careful', 'risk', 'warning', 'caution', 'don\'t']
        analysis.warnings = [p for p in analysis.key_points if any(kw in p.lower() for kw in warning_keywords)]
        
        analysis.cycle_phase = self.assess_cycle_phase(raw_text)
        analysis.risk_level = self.assess_risk_level(raw_text)
        
        if 'rate cut' in raw_text.lower() or 'easing' in raw_text.lower(): analysis.fed_policy_stance = "dovish"
        elif 'rate hike' in raw_text.lower() or 'tightening' in raw_text.lower(): analysis.fed_policy_stance = "hawkish"
        else: analysis.fed_policy_stance = "neutral"
        
        return analysis
