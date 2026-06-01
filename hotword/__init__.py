# coding: utf-8
"""
热词模块

提供热词替换和纠错功能，包括：
- PhonemeCorrector: 基于音素的纠错器
"""

import logging

logger = logging.getLogger('hotword')


from .hot_phoneme import PhonemeCorrector, CorrectionResult

__all__ = [
    'PhonemeCorrector',
    'CorrectionResult',
]

