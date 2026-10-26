/**
 * Skill Matcher Utility for TalentLens (Frontend)
 * Mirrors the backend skill extraction and calculation logic for fast local previews and testing.
 */

export const SKILLS_DATABASE = {
  programmingLanguages: [
    'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'c', 'go', 'golang',
    'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'dart', 'shell', 'bash'
  ],
  frameworksAndLibraries: [
    'react', 'react.js', 'reactjs', 'angular', 'vue', 'vue.js', 'vuejs', 'next.js', 'nextjs',
    'node.js', 'nodejs', 'express', 'express.js', 'django', 'flask', 'fastapi', 'spring',
    'spring boot', 'asp.net', '.net', 'laravel', 'ruby on rails', 'rails', 'tailwind',
    'bootstrap', 'redux', 'graphql', 'rest api', 'restful api'
  ],
  cloudAndDevOps: [
    'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud',
    'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins', 'ci/cd', 'git',
    'github', 'gitlab', 'linux', 'nginx', 'apache', 'cloudformation', 'serverless'
  ],
  databases: [
    'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'dynamodb',
    'cassandra', 'sqlite', 'oracle', 'elasticsearch', 'firebase', 'neo4j'
  ],
  aiAndDataScience: [
    'machine learning', 'deep learning', 'nlp', 'natural language processing',
    'computer vision', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
    'data analysis', 'data science', 'generative ai', 'llm', 'large language models',
    'bedrock', 'langchain', 'hugging face'
  ],
  softAndCoreSkills: [
    'agile', 'scrum', 'leadership', 'communication', 'problem solving',
    'system design', 'microservices', 'object-oriented programming', 'oop',
    'unit testing', 'test-driven development', 'tdd'
  ]
};

export const SKILL_ALIASES = {
  'js': 'javascript',
  'ts': 'typescript',
  'py': 'python',
  'reactjs': 'react',
  'react.js': 'react',
  'nodejs': 'node.js',
  'node': 'node.js',
  'k8s': 'kubernetes',
  'postgres': 'postgresql',
  'golang': 'go',
  'amazon web services': 'aws',
  'microsoft azure': 'azure',
  'google cloud': 'gcp',
  'ml': 'machine learning',
  'dl': 'deep learning'
};

/**
 * Clean and normalize text: lowercase, strip punctuation except dots/dashes/slashes useful in skill names
 * @param {string} text 
 * @returns {string}
 */
export function normalizeText(text) {
  if (!text || typeof text !== 'string') return '';
  return text
    .toLowerCase()
    .replace(/[\r\n\t]+/g, ' ')
    .replace(/[^\w\s\.\+#\/\-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Resolve an extracted skill term to its canonical name if an alias exists.
 * @param {string} skill 
 * @returns {string}
 */
function resolveSkillName(skill) {
  const lower = skill.toLowerCase().trim();
  return SKILL_ALIASES[lower] || lower;
}

/**
 * Extract matched skills from freeform text using the skills database.
 * @param {string} text 
 * @returns {string[]} List of unique detected canonical skills
 */
export function extractSkills(text) {
  if (!text || typeof text !== 'string') return [];
  const normalized = ` ${normalizeText(text)} `;
  const foundSkills = new Set();

  // Flatten all database skills
  const allSkills = Object.values(SKILLS_DATABASE).flat();

  // Add alias triggers to check
  const allTargets = Array.from(new Set([...allSkills, ...Object.keys(SKILL_ALIASES)]));

  for (const rawSkill of allTargets) {
    const skillNorm = rawSkill.toLowerCase().trim();
    // Escape special regex characters in the skill name
    const escaped = skillNorm.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    
    // Check with word boundaries or space boundaries
    const regex = new RegExp(`(^|[\\s,;()\\/.])${escaped}([\\s,;()\\/.)]|\$)`, 'i');
    if (regex.test(normalized)) {
      foundSkills.add(resolveSkillName(skillNorm));
    }
  }

  return Array.from(foundSkills);
}

/**
 * Compare resume text against job requirements text.
 * @param {string} resumeText 
 * @param {string} requirementsText 
 * @returns {{ matchPercentage: number, matchedSkills: string[], missingSkills: string[] }}
 */
export function matchSkills(resumeText, requirementsText) {
  const requiredSkills = extractSkills(requirementsText);

  // If no requirements were extracted from the text, return 0% match with empty lists
  if (requiredSkills.length === 0) {
    return {
      matchPercentage: 0,
      matchedSkills: [],
      missingSkills: []
    };
  }

  const candidateSkills = new Set(extractSkills(resumeText));
  const matched = [];
  const missing = [];

  for (const skill of requiredSkills) {
    if (candidateSkills.has(skill)) {
      matched.push(skill);
    } else {
      missing.push(skill);
    }
  }

  const matchPercentage = Math.round((matched.length / requiredSkills.length) * 100);

  return {
    matchPercentage,
    matchedSkills: matched.sort(),
    missingSkills: missing.sort()
  };
}
