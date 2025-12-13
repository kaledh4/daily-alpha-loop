#!/usr/bin/env python3
"""
Benjamin Cowen Methodology Preservation Pipeline
Processes video transcripts and extracts analytical patterns
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
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
        if self.historical_analogues is None:
            self.historical_analogues = []
        if self.key_indicators_mentioned is None:
            self.key_indicators_mentioned = []
        if self.key_points is None:
            self.key_points = []
        if self.cycle_logic is None:
            self.cycle_logic = []
        if self.warnings is None:
            self.warnings = []


class TranscriptProcessor:
    """Process Benjamin Cowen video transcripts"""
    
    # Pattern recognition for key concepts
    PATTERNS = {
        'fed_policy': [
            r'federal reserve',
            r'fed pivot',
            r'rate cuts?',
            r'rate hikes?',
            r'quantitative (?:easing|tightening)',
            r'QE|QT',
            r'm2 (?:money supply|growth)'
        ],
        'cycle_phase': [
            r'bull (?:market|run)',
            r'bear (?:market|run)',
            r'accumulation phase',
            r'euphori(?:a|c)',
            r'capitulation',
            r'mini bear'
        ],
        'metrics': [
            r'eth[/]btc',
            r'total3[/]btc',
            r'bitcoin dominance',
            r'mvrv',
            r'roi from (?:low|bottom)',
            r'diminishing returns',
            r'logarithmic regression'
        ],
        'historical': [
            r'2013 (?:cycle|top|bottom)',
            r'2017 (?:cycle|top|bottom)',
            r'2019 mini bear',
            r'2021 (?:cycle|top|bottom)',
            r'last cycle',
            r'previous (?:cycle|top|bottom)'
        ],
        'risk_warnings': [
            r'be careful',
            r'manage (?:your )?risk',
            r'not (?:financial )?advice',
            r'zoom out',
            r'don\'t get caught up',
            r'extremely (?:overbought|oversold)'
        ]
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
        """Extract pattern matches from text"""
        matches = []
        text_lower = text.lower()
        
        for pattern in self.PATTERNS.get(category, []):
            if re.search(pattern, text_lower):
                matches.append(pattern.replace(r'\b', '').replace('?', ''))
        
        return list(set(matches))
    
    def extract_metrics(self, text: str) -> Dict[str, Any]:
        """Extract numerical metrics from text"""
        metrics = {}
        
        # Bitcoin price
        btc_match = re.search(r'bitcoin.{0,50}?(\$?[\d,]+\.?\d*)[k ]', text.lower())
        if btc_match:
            price_str = btc_match.group(1).replace(',', '').replace('$', '')
            try:
                price = float(price_str)
                if 'k' in btc_match.group(0):
                    price *= 1000
                metrics['btc_price'] = price
            except ValueError:
                pass
        
        # ETH/BTC ratio
        eth_btc_match = re.search(r'eth[/]btc.{0,30}?(0\.\d+)', text.lower())
        if eth_btc_match:
            try:
                metrics['eth_btc_ratio'] = float(eth_btc_match.group(1))
            except ValueError:
                pass
        
        # M2 growth
        m2_match = re.search(r'm2.{0,30}?(-?\d+\.?\d*)%', text.lower())
        if m2_match:
            try:
                metrics['m2_yoy_growth'] = float(m2_match.group(1))
            except ValueError:
                pass
        
        # Fed funds rate
        ffr_match = re.search(r'federal funds rate.{0,30}?(\d+\.?\d*)%', text.lower())
        if ffr_match:
            try:
                metrics['fed_funds_rate'] = float(ffr_match.group(1))
            except ValueError:
                pass
        
        return metrics
    
    def extract_key_points(self, text: str, chunk_size: int = 1500) -> List[str]:
        """Extract key analytical points from text"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        key_points = []
        
        # Look for sentences with analytical weight
        importance_markers = [
            'important', 'key', 'critical', 'significant',
            'historically', 'typically', 'usually',
            'if we look at', 'what we see', 'what we\'re seeing',
            'the question is', 'the point is',
            'remember', 'keep in mind', 'don\'t forget'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
                
            sentence_lower = sentence.lower()
            if any(marker in sentence_lower for marker in importance_markers):
                key_points.append(sentence)
            
            # Also capture sentences with metrics
            if re.search(r'\d+\.?\d*%|\$[\d,]+|ratio|index|level', sentence_lower):
                key_points.append(sentence)
        
        return key_points[:20]  # Limit to top 20
    
    def assess_cycle_phase(self, text: str) -> str:
        """Determine discussed cycle phase"""
        text_lower = text.lower()
        
        phase_signals = {
            'accumulation': ['accumulation', 'bottom', 'capitulation', 'bear market bottom'],
            'bull_expansion': ['bull run', 'expansion', 'uptrend', 'rally'],
            'euphoria': ['euphoria', 'euphoric', 'top', 'peak', 'mania'],
            'bear': ['bear market', 'drawdown', 'correction', 'decline']
        }
        
        phase_scores = {}
        for phase, signals in phase_signals.items():
            phase_scores[phase] = sum(1 for signal in signals if signal in text_lower)
        
        if max(phase_scores.values()) == 0:
            return "neutral"
        
        return max(phase_scores, key=phase_scores.get)
    
    def assess_risk_level(self, text: str) -> str:
        """Assess implied risk level"""
        text_lower = text.lower()
        
        high_risk_signals = [
            'overbought', 'extended', 'elevated risk', 'be careful',
            'extreme', 'euphoria', 'top', 'caution'
        ]
        
        low_risk_signals = [
            'oversold', 'compressed', 'bottom', 'accumulation',
            'opportunity', 'undervalued'
        ]
        
        high_count = sum(1 for signal in high_risk_signals if signal in text_lower)
        low_count = sum(1 for signal in low_risk_signals if signal in text_lower)
        
        if high_count > low_count * 1.5:
            return "elevated"
        elif low_count > high_count * 1.5:
            return "compressed"
        else:
            return "neutral"
    
    def process_transcript(
        self, 
        raw_text: str, 
        video_id: str,
        title: str = "",
        upload_date: str = ""
    ) -> CycleAnalysis:
        """
        Process a transcript and extract methodology patterns
        
        Args:
            raw_text: Full video transcript
            video_id: YouTube video ID
            title: Video title
            upload_date: Upload date (YYYY-MM-DD)
        
        Returns:
            CycleAnalysis object with extracted data
        """
        analysis = CycleAnalysis(
            video_id=video_id,
            title=title,
            upload_date=upload_date,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Extract metrics
        metrics = self.extract_metrics(raw_text)
        for key, value in metrics.items():
            setattr(analysis, key, value)
        
        # Extract patterns
        analysis.historical_analogues = self.extract_patterns(raw_text, 'historical')
        analysis.key_indicators_mentioned = self.extract_patterns(raw_text, 'metrics')
        
        # Extract key points
        analysis.key_points = self.extract_key_points(raw_text)
        
        # Extract cycle logic (sentences about cycles)
        cycle_keywords = ['cycle', 'halving', 'bull', 'bear', 'top', 'bottom']
        analysis.cycle_logic = [
            point for point in analysis.key_points
            if any(kw in point.lower() for kw in cycle_keywords)
        ]
        
        # Extract warnings
        warning_keywords = ['careful', 'risk', 'warning', 'caution', 'don\'t']
        analysis.warnings = [
            point for point in analysis.key_points
            if any(kw in point.lower() for kw in warning_keywords)
        ]
        
        # Assess qualitative factors
        analysis.cycle_phase = self.assess_cycle_phase(raw_text)
        analysis.risk_level = self.assess_risk_level(raw_text)
        
        # Determine Fed stance
        if 'rate cut' in raw_text.lower() or 'easing' in raw_text.lower():
            analysis.fed_policy_stance = "dovish"
        elif 'rate hike' in raw_text.lower() or 'tightening' in raw_text.lower():
            analysis.fed_policy_stance = "hawkish"
        else:
            analysis.fed_policy_stance = "neutral"
        
        return analysis
    
    def save_analysis(self, analysis: CycleAnalysis):
        """Save analysis to JSON file"""
        output_file = self.transcripts_dir / f"{analysis.video_id}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(analysis), f, indent=2, default=str)
        
        print(f"✓ Saved analysis to {output_file}")
        return output_file
    
    def update_indicator_timeseries(self, analysis: CycleAnalysis):
        """Update time-series indicator files"""
        indicators = {
            'btc_price': analysis.btc_price,
            'eth_btc': analysis.eth_btc_ratio,
            'm2_yoy': analysis.m2_yoy_growth,
            'fed_funds_rate': analysis.fed_funds_rate
        }
        
        for indicator, value in indicators.items():
            if value is None:
                continue
            
            indicator_file = self.indicators_dir / f"{indicator}.json"
            
            # Load existing data
            if indicator_file.exists():
                with open(indicator_file, 'r') as f:
                    data = json.load(f)
            else:
                data = []
            
            # Append new data point
            data.append({
                'date': analysis.upload_date,
                'value': value,
                'video_id': analysis.video_id,
                'source': 'benjamin_cowen'
            })
            
            # Save updated data
            with open(indicator_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        print(f"✓ Updated indicator time-series")
    
    def generate_summary_report(self) -> str:
        """Generate summary of all processed transcripts"""
        analyses = []
        
        for file in self.transcripts_dir.glob("*.json"):
            with open(file, 'r') as f:
                analyses.append(json.load(f))
        
        if not analyses:
            return "No analyses found"
        
        report = f"""
# Benjamin Cowen Methodology Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- Total videos processed: {len(analyses)}
- Date range: {min(a['upload_date'] for a in analyses if a['upload_date'])} to {max(a['upload_date'] for a in analyses if a['upload_date'])}

## Most Common Historical References
"""
        
        # Count historical references
        all_refs = []
        for a in analyses:
            all_refs.extend(a.get('historical_analogues', []))
        
        from collections import Counter
        ref_counts = Counter(all_refs)
        
        for ref, count in ref_counts.most_common(10):
            report += f"- {ref}: {count} mentions\n"
        
        report += "\n## Most Mentioned Indicators\n"
        
        all_indicators = []
        for a in analyses:
            all_indicators.extend(a.get('key_indicators_mentioned', []))
        
        ind_counts = Counter(all_indicators)
        
        for ind, count in ind_counts.most_common(10):
            report += f"- {ind}: {count} mentions\n"
        
        return report


# Example usage
if __name__ == "__main__":
    processor = TranscriptProcessor()
    
    # Example: Process a transcript
    sample_transcript = """
    Today we're going to look at the ETH/BTC ratio and what it means for 
    the current cycle. If we compare to the 2017 cycle, we can see that 
    ETH/BTC typically peaks near the Bitcoin top. Right now we're at 0.038,
    which is elevated but not yet at euphoric levels. The Federal Reserve 
    just raised rates to 5.5%, which is putting pressure on risk assets.
    M2 growth is still negative year-over-year at -2.3%, which historically
    has been bearish for crypto. We need to be careful here and manage risk.
    Looking at diminishing returns, we shouldn't expect the same 20x from 
    the bottom like we saw in previous cycles. This could be more like the
    2019 mini bear before we see the next leg up, but that depends on Fed
    policy pivoting. Remember, it's all about risk management, not certainty.
    """
    
    analysis = processor.process_transcript(
        raw_text=sample_transcript,
        video_id="example_001",
        title="ETH/BTC Analysis - Current Cycle Update",
        upload_date="2024-03-15"
    )
    
    # Save results
    processor.save_analysis(analysis)
    processor.update_indicator_timeseries(analysis)
    
    # Print summary
    print("\nExtracted Analysis:")
    print(f"Cycle Phase: {analysis.cycle_phase}")
    print(f"Risk Level: {analysis.risk_level}")
    print(f"Fed Stance: {analysis.fed_policy_stance}")
    print(f"Historical Refs: {', '.join(analysis.historical_analogues[:3])}")
    print(f"\nKey Points ({len(analysis.key_points)}):")
    for i, point in enumerate(analysis.key_points[:5], 1):
        print(f"{i}. {point[:100]}...")
