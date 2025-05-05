# ACS 数据变量代码列表

本文档记录了从美国人口普查局的美国社区调查(American Community Survey, ACS)数据库中下载数据时使用的变量代码。这些代码用于获取人口统计、语言使用、种族和民族、年龄分布、性别比例、经济状况、住房情况等各类数据。

以下列出的代码按照主题分类整理，每个代码都对应特定的人口或社会经济指标。这些数据主要用于社区分析和研究目的。

## ACS 下载代码列表：



```txt

[
    "B15003_001E",  # Total population 25 years and over
    "B15003_002E",  # No schooling completed
    "B15003_003E",  # Nursery school
    "B15003_004E",  # Kindergarten
    "B15003_005E",  # 1st grade
    "B15003_006E",  # 2nd grade
    "B15003_007E",  # 3rd grade
    "B15003_008E",  # 4th grade
    "B15003_009E",  # 5th grade
    "B15003_010E",  # 6th grade
    "B15003_011E",  # 7th grade
    "B15003_012E"   # 8th grade
]


[
    "B15003_001E",  # Total population 25 years and over
    "B15003_017E"   # High school graduate (includes equivalency)
]

[
    "B15003_001E",  # Total population 25 years and over
    "B15003_022E"   # Bachelor's degree
]

[
    "B15003_001E",  # Total population 25 years and over
    "B15003_023E"   # Master's degree
]

[
    "B15003_001E",  # Total population 25 years and over
    "B15003_017E",  # High school graduate (includes equivalency)
    "B15003_018E",  # Some college, less than 1 year
    "B15003_019E",  # Some college, 1 or more years, no degree
    "B15003_020E",  # Associate's degree
    "B15003_021E",  # Associate's degree
    "B15003_022E",  # Bachelor's degree
    "B15003_023E",  # Master's degree
    "B15003_024E",  # Professional school degree
    "B15003_025E"   # Doctorate degree
]

[
    "C16001_001E",  # Total population 5 years and over
    "C16001_002E",  # English only
    "C16001_004E",  # Spanish: Speak English "very well"
    "C16001_007E",  # French, Haitian, Cajun: Speak English "very well"
    "C16001_010E",  # German, West Germanic: Speak English "very well"
    "C16001_013E",  # Russian, Slavic: Speak English "very well"
    "C16001_016E",  # Other Indo-European: Speak English "very well"
    "C16001_019E",  # Korean: Speak English "very well"
    "C16001_022E",  # Chinese: Speak English "very well"
    "C16001_025E",  # Vietnamese: Speak English "very well"
    "C16001_028E",  # Tagalog: Speak English "very well"
    "C16001_031E",  # Other Asian/Pacific Island: Speak English "very well"
    "C16001_034E",  # Arabic: Speak English "very well"
    "C16001_037E"   # Other/unspecified: Speak English "very well"
]

[
    "C16001_001E",  # Total population 5 years and over
    "C16001_003E"   # Total population who speak Spanish at home (regardless of English proficiency)
]

[
    "C16001_001E",  # Total population 5 years and over

    # Asian and Pacific Island language speakers (grouped by language, both "very well" and "less than very well")
    "C16001_019E", "C16001_020E",  # Korean
    "C16001_021E", "C16001_022E",  # Chinese (incl. Mandarin, Cantonese)
    "C16001_023E", "C16001_024E",  # Vietnamese
    "C16001_025E", "C16001_026E",  # Tagalog (incl. Filipino)
    "C16001_027E", "C16001_028E",  # Other Asian & Pacific Island
    "C16001_029E", "C16001_030E",  # More other Asian & Pacific Island
    "C16001_031E", "C16001_032E"   # More other Asian & Pacific Island
]


[
    "C16001_001E",  # Total population 5 years and over

    # Speak English "less than very well" (includes "not well" and "not at all")
    "C16001_005E",  # Spanish
    "C16001_008E",  # French, Haitian, Cajun
    "C16001_011E",  # German, other West Germanic
    "C16001_014E",  # Russian, Polish, other Slavic
    "C16001_017E",  # Other Indo-European
    "C16001_020E",  # Korean
    "C16001_023E",  # Chinese (incl. Mandarin, Cantonese)
    "C16001_026E",  # Vietnamese
    "C16001_029E",  # Tagalog
    "C16001_032E",  # Other Asian and Pacific Island languages
    "C16001_035E",  # Arabic
    "C16001_038E"   # Other and unspecified languages
]
--
[
    "B02001_001E",  # Total population
    "B02001_002E"   # White alone
]

[
    "B02001_001E",  # Total population
    "B02001_003E"   # Black or African American alone
]

[
    "B02001_001E",  # Total population
    "B02001_005E"   # Asian alone
]

[
    "B02001_001E",  # Total population
    "B02001_002E"   # White alone
]

[
    "B03003_001E",  # Total population
    "B03003_003E"   # Hispanic or Latino
]

[
    "B03002_001E",  # Total population
    "B03002_003E"   # White alone, not Hispanic or Latino
]

[
    "B03002_001E",  # Total population
    "B03002_004E"   # Black or African American alone, not Hispanic or Latino
]

[
    "B03002_001E",  # Total population
    "B03002_006E"   # Asian alone, not Hispanic or Latino
]

[
    "B03002_001E",  # Total population
    "B03002_003E"   # White alone, not Hispanic or Latino
]
--
[
    "B01001_001E",  # Total population
    "B01001_003E",  # Male under 5 years
    "B01001_027E"   # Female under 5 years
]

[
    "B01001_001E",  # 总人口
    "B01001_004E",  # 5至9岁（男性）
    "B01001_005E",  # 10至14岁（男性）
    "B01001_028E",  # 5至9岁（女性）
    "B01001_029E"   # 10至14岁（女性）
]

[
    "B01001_001E",  # Total population
    "B01001_006E",  # Male 15 to 17 years
    "B01001_007E",  # Male 18 and 19 years
    "B01001_008E",  # Male 20 years
    "B01001_009E",  # Male 21 years
    "B01001_010E",  # Male 22 to 24 years
    "B01001_030E",  # Female 15 to 17 years
    "B01001_031E",  # Female 18 and 19 years
    "B01001_032E",  # Female 20 years
    "B01001_033E",  # Female 21 years
    "B01001_034E"   # Female 22 to 24 years
]

[
    "B01001_001E",  # Total population

    # Male 18 to 64
    "B01001_007E",  # Male 18 and 19 years
    "B01001_008E",  # Male 20 years
    "B01001_009E",  # Male 21 years
    "B01001_010E",  # Male 22 to 24 years
    "B01001_011E",  # Male 25 to 29 years
    "B01001_012E",  # Male 30 to 34 years
    "B01001_013E",  # Male 35 to 39 years
    "B01001_014E",  # Male 40 to 44 years

    # Female 18 to 64
    "B01001_031E",  # Female 18 and 19 years
    "B01001_032E",  # Female 20 years
    "B01001_033E",  # Female 21 years
    "B01001_034E",  # Female 22 to 24 years
    "B01001_035E",  # Female 25 to 29 years
    "B01001_036E",  # Female 30 to 34 years
    "B01001_037E",  # Female 35 to 39 years
    "B01001_038E"   # Female 40 to 44 years
]

[
    "B01001_001E",  # Total population

    # Male 45 to 64
    "B01001_015E",  # Male 45 to 49 years
    "B01001_016E",  # Male 50 to 54 years
    "B01001_017E",  # Male 55 to 59 years
    "B01001_018E",  # Male 60 to 61 years
    "B01001_019E",  # Male 62 to 64 years

    # Female 45 to 64
    "B01001_039E",  # Female 45 to 49 years
    "B01001_040E",  # Female 50 to 54 years
    "B01001_041E",  # Female 55 to 59 years
    "B01001_042E",   # Female 60 to 61 years
    "B01001_043E"   # Female 62 to 64 years
]

[
    "B01001_001E",  # Total population

    # Male 65 and over
    "B01001_020E",  # Male 65 and 66 years
    "B01001_021E",  # Male 67 to 69 years
    "B01001_022E",  # Male 70 to 74 years
    "B01001_023E",  # Male 75 to 79 years
    "B01001_024E",  # Male 80 to 84 years
    "B01001_025E",  # Male 85 years and over

    # Female 65 and over
    "B01001_044E",  # Female 65 and 66 years
    "B01001_045E",  # Female 67 to 69 years
    "B01001_046E",  # Female 70 to 74 years
    "B01001_047E",  # Female 75 to 79 years
    "B01001_048E",  # Female 80 to 84 years
    "B01001_049E"   # Female 85 years and over
]

[
    "B01001_001E",  # Total population

    # Male 18 and over
    "B01001_007E",  # 18 and 19
    "B01001_008E",  # 20
    "B01001_009E",  # 21
    "B01001_010E",  # 22–24
    "B01001_011E",  # 25–29
    "B01001_012E",  # 30–34
    "B01001_013E",  # 35–39
    "B01001_014E",  # 40–44
    "B01001_015E",  # 45–49
    "B01001_016E",  # 50–54
    "B01001_017E",  # 55–59
    "B01001_018E",  # 60–61
    "B01001_019E",  # 62–64
    "B01001_020E",  # 65–66
    "B01001_021E",  # 67–69
    "B01001_022E",  # 70–74
    "B01001_023E",  # 75–79
    "B01001_024E",  # 80–84
    "B01001_025E",  # 85+

    # Female 18 and over
    "B01001_031E",  # 18 and 19
    "B01001_032E",  # 20
    "B01001_033E",  # 21
    "B01001_034E",  # 22–24
    "B01001_035E",  # 25–29
    "B01001_036E",  # 30–34
    "B01001_037E",  # 35–39
    "B01001_038E",  # 40–44
    "B01001_039E",  # 45–49
    "B01001_040E",  # 50–54
    "B01001_041E",  # 55–59
    "B01001_042E",  # 60–61
    "B01001_043E",  # 62–64
    "B01001_044E",  # 65–66
    "B01001_045E",  # 67–69
    "B01001_046E",  # 70–74
    "B01001_047E",  # 75–79
    "B01001_048E",  # 80–84
    "B01001_049E"   # 85+
]

[
    "B01001_001E",  # Total population

    # Male under 18
    "B01001_003E",  # Under 5
    "B01001_004E",  # 5–9
    "B01001_005E",  # 10–14
    "B01001_006E",  # 15–17

    # Female under 18
    "B01001_027E",  # Under 5
    "B01001_028E",  # 5–9
    "B01001_029E",  # 10–14
    "B01001_030E"   # 15–17
]
--
[
    "B01001_001E",  # Total population
    "B01001_002E"   # Total male population
]

[
    "B01001_001E",  # Total population
    "B01001_026E"   # Total female population
]

--
[
    "B17001_001E",  # Total population for whom poverty status is determined
    "B17001_002E"   # Population with income below poverty level in the past 12 months
]

[
    "B23025_004E",  # Civilian employed population (age 16+)
    "B23025_005E"   # Civilian unemployed population (age 16+)
]

[
    "B23025_004E",  # Civilian employed population (age 16+)
    "B23025_005E"   # Civilian unemployed population (age 16+)
]

[
    "B27001_001E",  # Total population

    # Male uninsured by age group
    "B27001_005E",  # Male under 6 years: No insurance
    "B27001_008E",  # Male 6–17 years: No insurance
    "B27001_011E",  # Male 18–24 years: No insurance
    "B27001_014E",  # Male 25–34 years: No insurance
    "B27001_017E",  # Male 35–44 years: No insurance
    "B27001_020E",  # Male 45–54 years: No insurance
    "B27001_023E",  # Male 55–64 years: No insurance
    "B27001_026E",  # Male 65–74 years: No insurance
    "B27001_029E",  # Male 75+ years: No insurance

    # Female uninsured by age group
    "B27001_033E",  # Female under 6 years: No insurance
    "B27001_036E",  # Female 6–17 years: No insurance
    "B27001_039E",  # Female 18–24 years: No insurance
    "B27001_042E",  # Female 25–34 years: No insurance
    "B27001_045E",  # Female 35–44 years: No insurance
    "B27001_048E",  # Female 45–54 years: No insurance
    "B27001_051E",  # Female 55–64 years: No insurance
    "B27001_054E",  # Female 65–74 years: No insurance
    "B27001_057E"   # Female 75+ years: No insurance
]

[
    "B27001_001E",  # 总人口数

    # 男性各年龄段有健康保险覆盖的人口数
    "B27001_004E",  # 男性，6岁以下
    "B27001_007E",  # 男性，6-18岁
    "B27001_010E",  # 男性，19-25岁
    "B27001_013E",  # 男性，26-34岁
    "B27001_016E",  # 男性，35-44岁
    "B27001_019E",  # 男性，45-54岁
    "B27001_022E",  # 男性，55-64岁
    "B27001_025E",  # 男性，65-74岁
    "B27001_028E",  # 男性，75岁及以上

    # 女性各年龄段有健康保险覆盖的人口数
    "B27001_032E",  # 女性，6岁以下
    "B27001_035E",  # 女性，6-18岁
    "B27001_038E",  # 女性，19-25岁
    "B27001_041E",  # 女性，26-34岁
    "B27001_044E",  # 女性，35-44岁
    "B27001_047E",  # 女性，45-54岁
    "B27001_050E",  # 女性，55-64岁
    "B27001_053E",  # 女性，65-74岁
    "B27001_056E"   # 女性，75岁及以上
]

[
    "B18101_001E",  # Total civilian noninstitutionalized population

    # Male with a disability by age
    "B18101_004E",  # Under 5
    "B18101_007E",  # 5–17
    "B18101_010E",  # 18–34
    "B18101_013E",  # 35–64
    "B18101_016E",  # 65–74
    "B18101_019E",  # 75+

    # Female with a disability by age
    "B18101_022E",  # Under 5
    "B18101_025E",  # 5–17
    "B18101_028E",  # 18–34
    "B18101_031E",  # 35–64
    "B18101_034E",  # 65–74
    "B18101_037E",  # 75+
]

[
    "B19301_001E"  # Per capita income in the past 12 months (inflation-adjusted dollars)
]

[
    "B19013_001E"  # Median household income in the past 12 months (in inflation-adjusted dollars)
]

[
    "B01003_001E"  # Total population
]
[
    "B19057_001E",  # Total number of households
    "B19057_002E"   # Households with public assistance income
]
[
    "B11005_001E",  # Total households
    "B11005_002E"   # Households with one or more people under 18 years
]
[
    "B11003_001E",  # Total families

    # Single-parent families with children
    "B11003_010E",  # Male householder, no wife present, with own children under 18
    "B11003_019E"   # Female householder, no husband present, with own children under 18
]
[
    "B11001_001E",  # Total households
    "B11001_006E"   # Female householder, no spouse present
]

[
    "B05002_001E",  # Total population
    "B05002_013E"   # Foreign born
]
[
    "B25024_001E",  # Total housing units

    # Multi-unit structures
    "B25024_004E",  # 2 units
    "B25024_005E",  # 3 or 4 units
    "B25024_006E",  # 5 to 9 units
    "B25024_007E",  # 10 to 19 units
    "B25024_008E",  # 20 to 49 units
    "B25024_009E"   # 50 or more units
]

[
    "B25049_001E",  # Total housing units
    "B25049_004E"   # Housing units lacking complete plumbing facilities
]

[
    "B25014_001E",  # Total occupied housing units

    # Owner-occupied units with >1.00 persons per room
    "B25014_005E",  # 1.01 to 1.50 persons per room
    "B25014_006E",  # More than 1.50 -2 persons per room
    "B25014_007E",  # More than 2.01 persons per room

    # Renter-occupied units with >1.00 persons per room
    "B25014_011E",  # 1.01 to 1.50 persons per room
    "B25014_012E",   # More than 1.50 persons per room
    "B25014_013E",  # More than 2.01 persons per room
]

[
    "B25003_001E",  # Total occupied housing units
    "B25003_003E"   # Renter-occupied housing units
]

[
    "B08201_001E",  # Total households
    "B08201_002E"   # Households with no vehicle available
]
[
    "B08201_001E",  # Total households
    "B08201_002E"   # Households with no vehicle available
]

[
    "B08303_001E"  # Mean travel time to work (in minutes)
]

[
    "B08301_001E",  # Total estimated workers 16 years and over 
    "B08301_021E"   # Worked at home
]

[
    "C24010_001E",  # Total civilian employed population 16 years and over
    "C24010_003E",  # Male: Management, business, science, and arts occupations
    "C24010_042E"   # Female: Management, business, science, and arts occupations
]

[
    "C24010_001E",  # Total civilian employed population 16 years and over
    "C24010_019E",  # Male: Service occupations
    "C24010_058E"   # Female: Service occupations
]

```

- test  
  