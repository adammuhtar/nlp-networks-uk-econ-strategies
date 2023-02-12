# Assessing policy co-ordination in government: text and network analysis of the UK’s economic strategies

This repository contains Python scripts used to extract and analyse texts from policy papers published by the UK government from March 2021 to July 2022 to identify the extent of UK's economic policy rollout. This work builds from [Coyle & Muhtar (2021)](https://www.bennettinstitute.cam.ac.uk/publications/industrial-policy-learning-past/), which analyse the extent of policy co-ordination and consistency among institutions responsible for policy crafting and delivery of industrial support measures in the UK (also often referred to as industrial policy). In particular, this notebook contains code to run text mining analysis on the take-up of policies announced under the 2021 [Plan for Growth](https://www.gov.uk/government/publications/build-back-better-our-plan-for-growth) and the 2021 [UK Innovation Strategy](https://www.gov.uk/government/publications/uk-innovation-strategy-leading-the-future-by-creating-it) among all publicly available UK Government policy papers (available from https://www.gov.uk/search/policy-papers-and-consultations)

The paper containing the full analysis is forthcoming at: Coyle, D. & Muhtar, A. (Forthcoming) "Assessing policy co-ordination in government: text and network analysis of the UK’s economic strategies"

## Data
The scraped dataset is stored in the following Kaggle dataset repository: https://www.kaggle.com/datasets/adammuhtar/uk-policy-paper-economic-strategy-term-frequency


This can be downloaded with the following command if the Kaggle API is available in your environment:
`kaggle datasets download -d adammuhtar/uk-policy-paper-economic-strategy-term-frequency`