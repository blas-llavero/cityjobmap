import type { OrganizationResult } from './overpass'

export type RelevanceLevel = 'high' | 'medium' | 'low'

export type OrganizationEvaluation = {
  score: number
  level: RelevanceLevel
  isRelevant: boolean
  matchedProfileIds: string[]
  matchedProfileLabels: string[]
  reasons: string[]
}

type SupportedLanguage =
  | 'en'
  | 'de'
  | 'fr'
  | 'it'
  | 'ca'
  | 'es'

type KeywordDictionary = Partial<
  Record<SupportedLanguage, string[]>
>

type ProfessionRule = {
  label: string

  keywords: KeywordDictionary

  directCategories?: string[]

  supportingCategories?: string[]

  educationProfile?: boolean
}

const PROFESSION_RULES: Record<
  string,
  ProfessionRule
> = {
  bioinformatics: {
    label: 'Bioinformàtica',

    keywords: {
      en: [
        'bioinformatics',
        'bioinformatician',
        'computational biology',
        'computational genomics',
        'genomics',
        'genomic',
        'proteomics',
        'biostatistics',
      ],

      de: [
        'bioinformatik',
        'bioinformatiker',
        'bioinformatikerin',
        'computational biology',
        'genomik',
        'proteomik',
      ],

      fr: [
        'bioinformatique',
        'bioinformaticien',
        'bioinformaticienne',
        'biologie computationnelle',
        'genomique',
        'genomique computationnelle',
        'proteomique',
      ],

      it: [
        'bioinformatica',
        'bioinformatico',
        'bioinformatica computazionale',
        'biologia computazionale',
        'genomica',
        'proteomica',
      ],

      ca: [
        'bioinformatica',
        'bioinformatic',
        'biologia computacional',
        'genomica',
        'proteomica',
      ],

      es: [
        'bioinformatica',
        'bioinformatico',
        'biologia computacional',
        'genomica',
        'proteomica',
      ],
    },

    supportingCategories: [
      'laboratori',
      'centre de recerca',
      'universitat',
    ],
  },

  it: {
    label: 'Informàtica',

    keywords: {
      en: [
        'computer science',
        'computer',
        'information technology',
        'it services',
        'it support',
        'software',
        'software development',
        'developer',
        'programming',
        'systems administrator',
        'system administrator',
        'network administrator',
        'networking',
        'cloud computing',
      ],

      de: [
        'informatik',
        'informatiker',
        'informatikerin',
        'informationstechnik',
        'it support',
        'it services',
        'softwareentwicklung',
        'softwareentwickler',
        'programmierung',
        'systemadministrator',
        'netzwerkadministrator',
      ],

      fr: [
        'informatique',
        'informaticien',
        'informaticienne',
        'technologies de information',
        'support informatique',
        'developpement logiciel',
        'developpeur',
        'programmation',
        'administrateur systeme',
        'administrateur reseau',
      ],

      it: [
        'informatica',
        'informatico',
        'tecnologie informatiche',
        'supporto informatico',
        'sviluppo software',
        'sviluppatore',
        'programmazione',
        'amministratore di sistema',
        'amministratore di rete',
      ],

      ca: [
        'informatica',
        'informatic',
        'tecnologies de la informacio',
        'suport informatic',
        'desenvolupament de programari',
        'programacio',
        'administrador de sistemes',
        'administrador de xarxes',
      ],

      es: [
        'informatica',
        'informatico',
        'tecnologias de la informacion',
        'soporte informatico',
        'desarrollo de software',
        'programacion',
        'administrador de sistemas',
        'administrador de redes',
      ],
    },

    directCategories: [
      'informatica',
    ],

    supportingCategories: [
      'electronica',
      'centre de recerca',
      'universitat',
      'centre de formacio',
    ],
  },

  cybersecurity: {
    label: 'Ciberseguretat',

    keywords: {
      en: [
        'cybersecurity',
        'cyber security',
        'information security',
        'network security',
        'security operations center',
        'soc analyst',
        'ethical hacking',
        'penetration testing',
      ],

      de: [
        'cybersicherheit',
        'cybersecurity',
        'it sicherheit',
        'informationssicherheit',
        'netzwerksicherheit',
        'security operations center',
        'penetrationstest',
      ],

      fr: [
        'cybersecurite',
        'securite informatique',
        'securite des systemes',
        'securite reseau',
        'soc analyst',
        'test intrusion',
      ],

      it: [
        'cybersicurezza',
        'sicurezza informatica',
        'sicurezza delle reti',
        'sicurezza dei sistemi',
        'soc analyst',
        'penetration test',
      ],

      ca: [
        'ciberseguretat',
        'seguretat informatica',
        'seguretat de xarxes',
        'seguretat de sistemes',
        'ethical hacking',
      ],

      es: [
        'ciberseguridad',
        'seguridad informatica',
        'seguridad de redes',
        'seguridad de sistemas',
        'hacking etico',
      ],
    },

    supportingCategories: [
      'informatica',
    ],
  },

  'math-teacher': {
    label: 'Professor/a de matemàtiques',

    educationProfile: true,

    keywords: {
      en: [
        'mathematics teacher',
        'math teacher',
        'maths teacher',
        'mathematics lecturer',
        'mathematics instructor',
        'mathematics',
      ],

      de: [
        'mathematiklehrer',
        'mathematiklehrerin',
        'lehrperson mathematik',
        'dozent mathematik',
        'dozentin mathematik',
        'mathematik',
      ],

      fr: [
        'professeur de mathematiques',
        'enseignant de mathematiques',
        'enseignante de mathematiques',
        'mathematiques',
      ],

      it: [
        'insegnante di matematica',
        'docente di matematica',
        'professore di matematica',
        'professoressa di matematica',
        'matematica',
      ],

      ca: [
        'professor de matematiques',
        'professora de matematiques',
        'docent de matematiques',
        'matematiques',
      ],

      es: [
        'profesor de matematicas',
        'profesora de matematicas',
        'docente de matematicas',
        'matematicas',
      ],
    },

    supportingCategories: [
      'centre educatiu',
      'centre de formacio',
      'universitat',
    ],
  },

  'computer-teacher': {
    label: "Professor/a d'informàtica",

    educationProfile: true,

    keywords: {
      en: [
        'computer science teacher',
        'computer teacher',
        'it teacher',
        'ict teacher',
        'computer science lecturer',
        'computer science instructor',
        'informatics teacher',
        'computer science',
        'informatics',
      ],

      de: [
        'informatiklehrer',
        'informatiklehrerin',
        'lehrperson informatik',
        'dozent informatik',
        'dozentin informatik',
        'informatikunterricht',
        'informatik',
      ],

      fr: [
        'professeur informatique',
        'professeur informatique',
        'enseignant informatique',
        'enseignante informatique',
        'professeur de informatique',
        'informatique',
      ],

      it: [
        'docente informatica',
        'docente di informatica',
        'insegnante informatica',
        'insegnante di informatica',
        'professore informatica',
        'informatica',
      ],

      ca: [
        'professor informatica',
        'professora informatica',
        'professor de informatica',
        'professora de informatica',
        'docent informatica',
        'informatica',
      ],

      es: [
        'profesor informatica',
        'profesora informatica',
        'profesor de informatica',
        'profesora de informatica',
        'docente informatica',
        'informatica',
      ],
    },

    supportingCategories: [
      'centre educatiu',
      'centre de formacio',
      'universitat',
    ],
  },

  'technology-teacher': {
    label: 'Professor/a de tecnologia',

    educationProfile: true,

    keywords: {
      en: [
        'technology teacher',
        'design technology teacher',
        'stem teacher',
        'robotics teacher',
        'technology education',
        'educational technology',
        'robotics',
      ],

      de: [
        'techniklehrer',
        'techniklehrerin',
        'lehrperson technik',
        'technikunterricht',
        'robotiklehrer',
        'robotik',
      ],

      fr: [
        'professeur de technologie',
        'enseignant technologie',
        'enseignante technologie',
        'professeur robotique',
        'robotique',
      ],

      it: [
        'insegnante tecnologia',
        'docente tecnologia',
        'docente di tecnologia',
        'insegnante robotica',
        'robotica',
      ],

      ca: [
        'professor tecnologia',
        'professora tecnologia',
        'docent tecnologia',
        'professor robotica',
        'robotica',
      ],

      es: [
        'profesor tecnologia',
        'profesora tecnologia',
        'docente tecnologia',
        'profesor robotica',
        'robotica',
      ],
    },

    supportingCategories: [
      'centre educatiu',
      'centre de formacio',
      'universitat',
    ],
  },

  'electricity-teacher': {
    label: "Professor/a d'electricitat",

    educationProfile: true,

    keywords: {
      en: [
        'electrical teacher',
        'electrical engineering teacher',
        'electrical instructor',
        'electrical lecturer',
        'electrical engineering',
        'electricity',
      ],

      de: [
        'elektrotechniklehrer',
        'lehrperson elektrotechnik',
        'dozent elektrotechnik',
        'elektrotechnik',
        'elektrik',
      ],

      fr: [
        'professeur electricite',
        'enseignant electricite',
        'professeur electrotechnique',
        'electrotechnique',
        'electricite',
      ],

      it: [
        'docente elettrotecnica',
        'insegnante elettrotecnica',
        'docente elettricita',
        'elettrotecnica',
        'elettricita',
      ],

      ca: [
        'professor electricitat',
        'professora electricitat',
        'docent electricitat',
        'electrotecnica',
        'electricitat',
      ],

      es: [
        'profesor electricidad',
        'profesora electricidad',
        'docente electricidad',
        'electrotecnica',
        'electricidad',
      ],
    },

    directCategories: [
      'empresa d electricitat',
    ],

    supportingCategories: [
      'centre educatiu',
      'centre de formacio',
    ],
  },

  'electronics-teacher': {
    label: "Professor/a d'electrònica",

    educationProfile: true,

    keywords: {
      en: [
        'electronics teacher',
        'electronics instructor',
        'electronics lecturer',
        'electronic engineering teacher',
        'electronics',
        'electronic engineering',
      ],

      de: [
        'elektroniklehrer',
        'lehrperson elektronik',
        'dozent elektronik',
        'elektronik',
        'elektroniktechnik',
      ],

      fr: [
        'professeur electronique',
        'enseignant electronique',
        'electronique',
        'ingenierie electronique',
      ],

      it: [
        'docente elettronica',
        'insegnante elettronica',
        'elettronica',
        'ingegneria elettronica',
      ],

      ca: [
        'professor electronica',
        'professora electronica',
        'docent electronica',
        'electronica',
      ],

      es: [
        'profesor electronica',
        'profesora electronica',
        'docente electronica',
        'electronica',
      ],
    },

    directCategories: [
      'electronica',
    ],

    supportingCategories: [
      'centre educatiu',
      'centre de formacio',
    ],
  },
}

function normalizeText(
  text: string,
): string {
  return text
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLocaleLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
}

function normalizeSelectedLanguages(
  languages: string[],
): SupportedLanguage[] {
  const supported: SupportedLanguage[] = [
    'en',
    'de',
    'fr',
    'it',
    'ca',
    'es',
  ]

  const result = languages.filter(
    (language): language is SupportedLanguage =>
      supported.includes(
        language as SupportedLanguage,
      ),
  )

  return result.length > 0
    ? result
    : ['en']
}

function getKeywordsForLanguages(
  dictionary: KeywordDictionary,
  selectedLanguages: SupportedLanguage[],
): string[] {
  const terms = new Set<string>()

  for (const language of selectedLanguages) {
    for (
      const keyword
      of dictionary[language] ?? []
    ) {
      terms.add(keyword)
    }
  }

  return [...terms]
}

function getMatchingKeywords(
  text: string,
  keywords: string[],
): string[] {
  return keywords.filter(
    (keyword) =>
      text.includes(
        normalizeText(keyword),
      ),
  )
}

function categoryMatches(
  category: string,
  categories: string[] | undefined,
): boolean {
  if (!categories) {
    return false
  }

  const normalizedCategory =
    normalizeText(category)

  return categories.some(
    (candidate) =>
      normalizedCategory.includes(
        normalizeText(candidate),
      ),
  )
}

function isEducationalOrganization(
  organization: OrganizationResult,
): boolean {
  const category =
    normalizeText(
      organization.category,
    )

  return [
    'centre educatiu',
    'centre de formacio',
    'universitat',
    'school',
    'college',
    'university',
    'training',
  ].some(
    (keyword) =>
      category.includes(
        normalizeText(keyword),
      ),
  )
}

function getDistanceBonus(
  distanceKm: number | null,
): number {
  if (distanceKm === null) {
    return 0
  }

  if (distanceKm <= 5) {
    return 8
  }

  if (distanceKm <= 20) {
    return 6
  }

  if (distanceKm <= 40) {
    return 4
  }

  if (distanceKm <= 60) {
    return 2
  }

  return 1
}

function evaluateProfile(
  organization: OrganizationResult,
  rule: ProfessionRule,
  selectedLanguages: SupportedLanguage[],
): {
  score: number
  reasons: string[]
} {
  const searchableText =
    normalizeText(
      [
        organization.name,
        organization.category,
        organization.searchableText,
      ].join(' '),
    )

  const keywords =
    getKeywordsForLanguages(
      rule.keywords,
      selectedLanguages,
    )

  const keywordMatches =
    getMatchingKeywords(
      searchableText,
      keywords,
    )

  const directCategoryMatch =
    categoryMatches(
      organization.category,
      rule.directCategories,
    )

  const supportingCategoryMatch =
    categoryMatches(
      organization.category,
      rule.supportingCategories,
    )

  const educationalOrganization =
    isEducationalOrganization(
      organization,
    )

  const reasons: string[] = []
  let score = 0

  if (keywordMatches.length > 0) {
    score += Math.min(
      62,
      34 +
        (keywordMatches.length - 1) * 7,
    )

    reasons.push(
      `Paraules relacionades: ${
        keywordMatches
          .slice(0, 3)
          .join(', ')
      }`,
    )
  }

  if (directCategoryMatch) {
    score += 36

    reasons.push(
      `Categoria directament compatible: ${organization.category}`,
    )
  }

  /*
   * Per als perfils docents, ser simplement
   * una escola o una acadèmia NO és suficient.
   *
   * Primer ha d'existir alguna evidència
   * de la matèria: informàtica, matemàtiques,
   * electrònica, etc.
   */
  if (rule.educationProfile) {
    const hasSubjectEvidence =
      keywordMatches.length > 0 ||
      directCategoryMatch

    if (
      hasSubjectEvidence &&
      educationalOrganization
    ) {
      score += 24

      reasons.push(
        'És un centre educatiu i hi ha evidència de la matèria',
      )
    }

    if (!hasSubjectEvidence) {
      return {
        score: 0,
        reasons: [],
      }
    }
  } else if (
    supportingCategoryMatch &&
    keywordMatches.length > 0
  ) {
    score += 12

    reasons.push(
      `Categoria compatible: ${organization.category}`,
    )
  }

  /*
   * Una categoria de suport sola no converteix
   * una universitat o centre de recerca en
   * bioinformàtica o informàtica.
   */
  if (
    !rule.educationProfile &&
    keywordMatches.length === 0 &&
    !directCategoryMatch
  ) {
    return {
      score: 0,
      reasons: [],
    }
  }

  return {
    score,
    reasons,
  }
}

export function evaluateOrganization(
  organization: OrganizationResult,
  selectedProfessionIds: string[],
  selectedLanguageCodes: string[] = ['en'],
): OrganizationEvaluation {
  const selectedLanguages =
    normalizeSelectedLanguages(
      selectedLanguageCodes,
    )

  let highestProfileScore = 0

  const matchedProfileIds: string[] = []
  const matchedProfileLabels: string[] = []
  const reasons = new Set<string>()

  for (
    const professionId
    of selectedProfessionIds
  ) {
    const rule =
      PROFESSION_RULES[
        professionId
      ]

    if (!rule) {
      continue
    }

    const result = evaluateProfile(
      organization,
      rule,
      selectedLanguages,
    )

    if (result.score <= 0) {
      continue
    }

    matchedProfileIds.push(
      professionId,
    )

    matchedProfileLabels.push(
      rule.label,
    )

    highestProfileScore =
      Math.max(
        highestProfileScore,
        result.score,
      )

    for (
      const reason
      of result.reasons
    ) {
      reasons.add(reason)
    }
  }

  let score =
    highestProfileScore

  if (
    matchedProfileIds.length > 1
  ) {
    score += Math.min(
      12,
      (
        matchedProfileIds.length -
        1
      ) * 4,
    )
  }

  if (score > 0) {
    score += getDistanceBonus(
      organization.distanceKm,
    )

    if (organization.website) {
      score += 4

      reasons.add(
        'Disposa d’una pàgina web indicada',
      )
    }
  }

  score = Math.min(
    100,
    Math.round(score),
  )

  const level: RelevanceLevel =
    score >= 65
      ? 'high'
      : score >= 30
        ? 'medium'
        : 'low'

  return {
    score,
    level,
    isRelevant: score >= 30,
    matchedProfileIds,
    matchedProfileLabels,
    reasons: [...reasons],
  }
}