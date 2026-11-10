# NUDGE OCR Evaluation Report

## Method
Manually transcribed reference text is compared with OCR raw_text. All legible text, including wordmarks, handwritten slogans and text on illustrated clothing, is included. QR-code payloads and unreadable text are excluded.
Unicode NFKC normalization, case-folding and whitespace normalization are applied. Punctuation is retained.
Words are tokenized by splitting on whitespace. CER and WER aggregates are pooled: total edit errors divided by total reference characters or words, respectively.
An entirely empty OCR result is valid only when raw_text is empty, confidence is an empty array and overall_confidence is null; it is scored normally against the non-empty reference.
OCR outputs were produced using EasyOCR. The historical pipeline resized images narrower than 1600 px to 1600 px width using cubic interpolation. The archived outputs were recovered from Git commit d4760d4; OCR was not rerun for this evaluation.
Ground-truth references are provisional pending final human review.

CER = character edit distance / reference character count.
WER = word edit distance / reference word count.

## Per-image results

| Image | CER | WER | OCR confidence | Regions |
|---|---:|---:|---:|---:|
| payment_notice.png | 0.0585 | 0.1077 | 0.8946 | 26 |
| screenshot 2.jpeg | 0.1100 | 0.5000 | 0.7989 | 14 |
| screenshot 3.jpeg | 0.1172 | 0.2105 | 0.8170 | 37 |
| screenshot 4.jpeg | 0.4027 | 0.5000 | 0.7243 | 30 |
| screenshot 5.jpeg | 0.2387 | 0.4545 | 0.7500 | 22 |
| screenshot 6.jpeg | 0.0207 | 0.0868 | 0.7983 | 77 |
| screenshot 7.jpeg | 0.5006 | 0.7227 | 0.4169 | 74 |
| screenshot 8.jpeg | 0.1764 | 0.5686 | 0.6805 | 87 |
| screenshot 9.jpeg | 0.1614 | 0.4810 | 0.6024 | 34 |

## Aggregate results

- Ground-truth cases: 9
- Aggregate CER: 0.1484 (14.84%)
- Aggregate WER: 0.2926 (29.26%)

## Limitations

- OCR confidence is a model confidence estimate, not an accuracy metric.
- Reference transcriptions are provisional and require final human review.
- QR-code payloads and unreadable text are excluded; legible wordmarks, handwritten slogans and text on illustrated clothing are included.
- Nine images are not sufficient to establish general OCR performance.
- Reference line ordering affects edit-distance results.
- CER and WER do not indicate whether critical fields such as dates, times or names were transcribed correctly.
- OCR engine and image-processing dependency versions are not pinned, so fresh OCR runs may differ.
- The pooled aggregate is character- and word-weighted; larger images contribute more. The unweighted mean of per-image rates is approximately 19.9% CER and 40.4% WER.
