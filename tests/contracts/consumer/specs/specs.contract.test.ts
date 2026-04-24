/**
 * Specifications API Contract Tests
 *
 * Consumer: TraceRTM-Web
 * Provider: TraceRTM-API
 * Domain: Specification Analytics
 */

import { describe, it, beforeAll, afterAll } from 'vitest';
import {
  createPactProvider,
  setupPact,
  teardownPact,
  like,
  eachLike,
  uuid,
  integer,
  decimal,
  errorResponse,
  standardResponse,
  withAuth,
} from '../setup';

const provider = createPactProvider('TraceRTM-Web-Specs');

describe('Specifications Contract Tests', () => {
  beforeAll(async () => {
    await setupPact(provider);
  });

  afterAll(async () => {
    await teardownPact(provider);
  });

  describe('POST /api/v1/spec-analytics/analyze', () => {
    it('should analyze specification text', async () => {
      await provider.addInteraction({
        states: [{ description: 'user is authenticated' }],
        uponReceiving: 'a request to analyze specification',
        withRequest: {
          method: 'POST',
          path: '/api/v1/spec-analytics/analyze',
          headers: withAuth(),
          body: {
            text: 'The system SHALL provide user authentication',
            type: 'requirement',
          },
        },
        willRespondWith: standardResponse({
          id: uuid('spec-123'),
          text: like('The system SHALL provide user authentication'),
          analysis: {
            earsPattern: like('Ubiquitous'),
            quality: {
              clarity: decimal(0.85),
              completeness: decimal(0.90),
              consistency: decimal(0.95),
              testability: decimal(0.88),
            },
            issues: eachLike({
              type: like('ambiguity'),
              severity: like('medium'),
              message: like('Consider clarifying authentication method'),
              suggestion: like('Specify authentication mechanism (OAuth, JWT, etc.)'),
            }),
            metrics: {
              wordCount: integer(7),
              complexityScore: decimal(0.3),
            },
          },
        }),
      });

      const response = await fetch('http://localhost:8080/api/v1/spec-analytics/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({
          text: 'The system SHALL provide user authentication',
          type: 'requirement',
        }),
      });

      console.assert(response.status === 200);
    });
  });

  describe('POST /api/v1/spec-analytics/batch-analyze', () => {
    it('should analyze multiple specifications', async () => {
      await provider.addInteraction({
        states: [{ description: 'user is authenticated' }],
        uponReceiving: 'a request to batch analyze specifications',
        withRequest: {
          method: 'POST',
          path: '/api/v1/spec-analytics/batch-analyze',
          headers: withAuth(),
          body: {
            specifications: [
              { id: 'spec-1', text: 'The system SHALL authenticate users' },
              { id: 'spec-2', text: 'WHEN user logs in THEN system validates credentials' },
            ],
          },
        },
        willRespondWith: standardResponse({
          results: eachLike({
            id: like('spec-1'),
            analysis: {
              earsPattern: like('Ubiquitous'),
              quality: {
                clarity: decimal(0.85),
                completeness: decimal(0.90),
                consistency: decimal(0.95),
                testability: decimal(0.88),
              },
            },
          }),
          summary: {
            total: integer(2),
            passed: integer(2),
            failed: integer(0),
            averageQuality: decimal(0.89),
          },
        }),
      });

      const response = await fetch('http://localhost:8080/api/v1/spec-analytics/batch-analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({
          specifications: [
            { id: 'spec-1', text: 'The system SHALL authenticate users' },
            { id: 'spec-2', text: 'WHEN user logs in THEN system validates credentials' },
          ],
        }),
      });

      console.assert(response.status === 200);
    });
  });

  describe('GET /api/v1/spec-analytics/ears-patterns', () => {
    it('should return EARS pattern examples', async () => {
      await provider.addInteraction({
        states: [],
        uponReceiving: 'a request for EARS patterns',
        withRequest: {
          method: 'GET',
          path: '/api/v1/spec-analytics/ears-patterns',
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          patterns: eachLike({
            name: like('Ubiquitous'),
            template: like('The system SHALL <requirement>'),
            description: like('Requirements that apply across all modes'),
            examples: eachLike(like('The system SHALL validate user input')),
          }),
        }),
      });

      const response = await fetch('http://localhost:8080/api/v1/spec-analytics/ears-patterns', {
        headers: { Authorization: 'Bearer test-token' },
      });

      console.assert(response.status === 200);
    });
  });

  describe('POST /api/v1/spec-analytics/validate-iso29148', () => {
    it('should validate against ISO 29148 standard', async () => {
      await provider.addInteraction({
        states: [{ description: 'user is authenticated' }],
        uponReceiving: 'a request to validate ISO 29148 compliance',
        withRequest: {
          method: 'POST',
          path: '/api/v1/spec-analytics/validate-iso29148',
          headers: withAuth(),
          body: {
            specifications: [
              { id: 'spec-1', text: 'The system SHALL authenticate users' },
            ],
          },
        },
        willRespondWith: standardResponse({
          compliant: like(true),
          score: decimal(0.92),
          violations: eachLike({
            specId: like('spec-1'),
            rule: like('ISO-29148-5.2.5'),
            severity: like('medium'),
            message: like('Consider adding acceptance criteria'),
          }),
          recommendations: eachLike({
            category: like('clarity'),
            message: like('Add measurable acceptance criteria'),
          }),
        }),
      });

      const response = await fetch(
        'http://localhost:8080/api/v1/spec-analytics/validate-iso29148',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token',
          },
          body: JSON.stringify({
            specifications: [
              { id: 'spec-1', text: 'The system SHALL authenticate users' },
            ],
          }),
        }
      );

      console.assert(response.status === 200);
    });
  });
});
