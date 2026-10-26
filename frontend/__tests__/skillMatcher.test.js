import { describe, it, expect } from 'vitest';
import { normalizeText, extractSkills, matchSkills } from '../src/utils/skillMatcher.js';

describe('SkillMatcher Utility Tests', () => {
  describe('normalizeText', () => {
    it('should lowercase and clean extra whitespace and punctuation', () => {
      const input = '  Senior   Software Engineer, with React & Node.js!  ';
      const result = normalizeText(input);
      expect(result).toBe('senior software engineer with react node.js');
    });

    it('should return empty string for null, undefined, or empty inputs', () => {
      expect(normalizeText(null)).toBe('');
      expect(normalizeText(undefined)).toBe('');
      expect(normalizeText('')).toBe('');
    });
  });

  describe('extractSkills', () => {
    it('should extract canonical skills accurately from a text paragraph', () => {
      const text = 'Experienced in Python, Docker, and PostgreSQL databases.';
      const skills = extractSkills(text);
      expect(skills).toContain('python');
      expect(skills).toContain('docker');
      expect(skills).toContain('postgresql');
    });

    it('should resolve skill aliases correctly', () => {
      const text = 'Proficient in JS, TS, K8s, and AWS cloud computing';
      const skills = extractSkills(text);
      expect(skills).toContain('javascript'); // js -> javascript
      expect(skills).toContain('typescript'); // ts -> typescript
      expect(skills).toContain('kubernetes'); // k8s -> kubernetes
      expect(skills).toContain('aws');        // aws is a canonical skill
    });

    it('should be case insensitive', () => {
      const text = 'REACT, python, DOCKER';
      const skills = extractSkills(text);
      expect(skills).toContain('react');
      expect(skills).toContain('python');
      expect(skills).toContain('docker');
    });
  });

  describe('matchSkills', () => {
    it('should return 100% match when all required skills are present in resume', () => {
      const requirements = 'Looking for Python and Docker developer.';
      const resume = '5 years of Python experience developing Docker containers.';
      const result = matchSkills(resume, requirements);

      expect(result.matchPercentage).toBe(100);
      expect(result.matchedSkills).toEqual(['docker', 'python']);
      expect(result.missingSkills).toEqual([]);
    });

    it('should return 0% match when none of the required skills are in resume', () => {
      const requirements = 'Requirements: Kubernetes, Rust, Terraform';
      const resume = 'Experienced in Sales, Operations, and Customer Support.';
      const result = matchSkills(resume, requirements);

      expect(result.matchPercentage).toBe(0);
      expect(result.matchedSkills).toEqual([]);
      expect(result.missingSkills).toContain('kubernetes');
      expect(result.missingSkills).toContain('rust');
      expect(result.missingSkills).toContain('terraform');
    });

    it('should calculate partial matches correctly', () => {
      const requirements = 'Must have Python, React, Docker, and Kubernetes.';
      const resume = 'Experienced with Python and React.';
      const result = matchSkills(resume, requirements);

      expect(result.matchPercentage).toBe(50);
      expect(result.matchedSkills).toEqual(['python', 'react']);
      expect(result.missingSkills).toEqual(['docker', 'kubernetes']);
    });

    it('should handle edge cases with empty requirements gracefully', () => {
      const requirements = 'Looking for an enthusiastic teammate.';
      const resume = 'Python developer.';
      const result = matchSkills(resume, requirements);

      expect(result.matchPercentage).toBe(0);
      expect(result.matchedSkills).toEqual([]);
      expect(result.missingSkills).toEqual([]);
    });

    it('should handle aliases across match evaluations', () => {
      const requirements = 'Job requires Javascript and Postgres.';
      const resume = 'Skilled in JS and PostgreSQL.';
      const result = matchSkills(resume, requirements);

      expect(result.matchPercentage).toBe(100);
      expect(result.matchedSkills).toContain('javascript');
      expect(result.matchedSkills).toContain('postgresql');
      expect(result.missingSkills).toHaveLength(0);
    });
  });
});
