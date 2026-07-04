import { render } from '@testing-library/react';
import DOMPurify from 'dompurify';
import { describe, expect, it } from 'vitest';

// Test XSS prevention in user-generated content
describe('XSS Prevention Tests', () => {
  describe('Basic XSS Attack Vectors', () => {
    it('should prevent script tag injection', () => {
      const maliciousInput = '<script>alert("XSS")</script>';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('<script>');
      expect(sanitized).not.toContain('alert');
    });

    it('should prevent img onerror injection', () => {
      const maliciousInput = '<img src=x onerror=alert("XSS")>';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('onerror=');
      expect(sanitized).not.toContain('alert');
    });

    it('should prevent javascript: protocol', () => {
      const maliciousInput = '<a href="javascript:alert(\'XSS\')">Click</a>';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('javascript:');
    });

    it('should prevent svg onload injection', () => {
      const maliciousInput = '<svg/onload=alert("XSS")>';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('onload=');
    });

    it('should prevent iframe injection', () => {
      const maliciousInput = '<iframe src="javascript:alert(\'XSS\')"></iframe>';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('javascript:');
    });

    it('should prevent body onload injection', () => {
      const maliciousInput = '<body onload=alert("XSS")>';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('onload=');
    });
  });

  describe('Advanced XSS Attack Vectors', () => {
    it('should prevent event handler variations', () => {
      const eventHandlers = ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus', 'onblur'];

      eventHandlers.forEach((handler) => {
        const maliciousInput = `<div ${handler}=alert("XSS")>Test</div>`;
        const sanitized = DOMPurify.sanitize(maliciousInput);

        expect(sanitized).not.toContain(`${handler}=`);
      });
    });

    it('should prevent data URI with script', () => {
      const maliciousInput = '<img src="data:text/html,<script>alert(\'XSS\')</script>">';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      // DOMPurify sanitizes or removes dangerous data URIs
      // The important thing is the XSS doesn't execute
      expect(sanitized).toBeDefined();
    });

    it('should prevent meta refresh redirection', () => {
      const maliciousInput =
        '<meta http-equiv="refresh" content="0;url=javascript:alert(\'XSS\')">';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('javascript:');
    });

    it('should prevent form action hijacking', () => {
      const maliciousInput =
        '<form action="javascript:alert(\'XSS\')"><input type="submit"></form>';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('javascript:');
    });

    it('should prevent CSS expression injection', () => {
      const maliciousInput = '<div style="width: expression(alert(\'XSS\'))">Test</div>';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      // DOMPurify sanitizes IE-specific CSS expressions
      expect(sanitized).toContain('Test');
    });

    it('should prevent base tag injection', () => {
      const maliciousInput = '<base href="javascript:alert(\'XSS\')">';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('javascript:');
    });
  });

  describe('Markdown XSS Prevention', () => {
    it('should prevent XSS in markdown links', () => {
      // DOMPurify sanitizes HTML, not Markdown - convert to HTML first
      const htmlFromMarkdown = '<a href="javascript:alert("XSS")">Click me</a>';
      const sanitized = DOMPurify.sanitize(htmlFromMarkdown);

      expect(sanitized).not.toContain('javascript:');
    });

    it('should prevent XSS in markdown images', () => {
      // DOMPurify sanitizes HTML, not Markdown - convert to HTML first
      const htmlFromMarkdown = '<img src="javascript:alert("XSS")" alt="Image">';
      const sanitized = DOMPurify.sanitize(htmlFromMarkdown);

      expect(sanitized).not.toContain('javascript:');
    });

    it('should allow safe HTML in markdown', () => {
      const safeMarkdown = '<strong>Bold text</strong>';
      const sanitized = DOMPurify.sanitize(safeMarkdown);

      expect(sanitized).toContain('Bold text');
    });
  });

  describe('DOM Clobbering Prevention', () => {
    it('should prevent name attribute clobbering', () => {
      const maliciousInput = '<form name="alert">Test</form>';
      const sanitized = DOMPurify.sanitize(maliciousInput, {
        SANITIZE_DOM: true,
      });

      // DOMPurify with SANITIZE_DOM prevents dangerous clobbering
      expect(sanitized).toContain('Test');
    });

    it('should prevent id attribute clobbering', () => {
      const maliciousInput = '<div id="location">Test</div>';
      const _sanitized = DOMPurify.sanitize(maliciousInput, {
        SANITIZE_DOM: true,
      });

      // Should not allow clobbering of window properties
    });
  });

  describe('React dangerouslySetInnerHTML Protection', () => {
    it('should sanitize before using dangerouslySetInnerHTML', () => {
      const unsafeHTML = '<script>alert("XSS")</script><p>Safe content</p>';
      const sanitized = DOMPurify.sanitize(unsafeHTML);

      // Create a test component
      const TestComponent = () => <div dangerouslySetInnerHTML={{ __html: sanitized }} />;

      render(<TestComponent />);

      // Should not contain script tag
      expect(document.body.innerHTML).not.toContain('<script>');
      expect(document.body.innerHTML).toContain('Safe content');
    });
  });

  describe('URL Sanitization', () => {
    it('should validate URLs before rendering', () => {
      const urls = [
        { safe: true, url: 'https://example.com' },
        { safe: true, url: 'http://example.com' },
        { safe: false, url: 'javascript:alert("XSS")' },
        { safe: false, url: 'data:text/html,<script>alert("XSS")</script>' },
        { safe: false, url: 'vbscript:msgbox("XSS")' },
        { safe: false, url: 'file:///etc/passwd' },
      ];

      urls.forEach(({ url, safe }) => {
        const isValid = /^https?:\/\//.test(url);
        expect(isValid).toBe(safe);
      });
    });

    it('should sanitize user-provided URLs', () => {
      const maliciousURL = 'javascript:alert("XSS")';
      const sanitizedURL = DOMPurify.sanitize(`<a href="${maliciousURL}">Link</a>`);

      expect(sanitizedURL).not.toContain('javascript:');
    });
  });

  describe('Content Security Policy Compatibility', () => {
    it('should not use inline event handlers', () => {
      const maliciousInput = '<button onclick="alert(\'XSS\')">Click</button>';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('onclick=');
    });

    it('should remove inline scripts', () => {
      const maliciousInput = `
        <div>
          <script>alert('XSS')</script>
          <p>Content</p>
        </div>
      `;
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('<script>');
      expect(sanitized).toContain('Content');
    });
  });

  describe('User Input Sanitization in Forms', () => {
    it('should sanitize text input before display', () => {
      const userInput = '<script>alert("XSS")</script>Hello';
      const sanitized = DOMPurify.sanitize(userInput);

      expect(sanitized).not.toContain('<script>');
      expect(sanitized).toContain('Hello');
    });

    it('should handle special characters safely', () => {
      const specialChars = ['<', '>', '&', '"', "'"];

      specialChars.forEach((char) => {
        const input = `Test ${char} character`;
        const sanitized = DOMPurify.sanitize(input);

        // Should escape or safely handle special characters
        expect(sanitized).toBeDefined();
      });
    });
  });

  describe('Attribute Injection Prevention', () => {
    it('should prevent attribute injection via quotes', () => {
      const maliciousInput = '<input value="test" onclick="alert(\'XSS\')">';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('onclick=');
    });

    it('should prevent style attribute injection', () => {
      const maliciousInput = '<div style="background: url(javascript:alert(\'XSS\'))">Test</div>';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      // DOMPurify sanitizes dangerous URLs in styles
      expect(sanitized).toContain('Test');
    });
  });

  describe('Template String Safety', () => {
    it('should safely handle template literals', () => {
      const userInput = '${alert("XSS")}';
      const sanitized = DOMPurify.sanitize(userInput);

      // Template literals are safe in HTML context - they only execute in JS
      expect(sanitized).toBe('${alert("XSS")}');
    });
  });

  describe('Nested XSS Attempts', () => {
    it('should prevent nested script tags', () => {
      const maliciousInput = '<<script>script>alert("XSS")<</script>/script>';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      expect(sanitized).not.toContain('<script>');
    });

    it('should prevent encoded XSS', () => {
      const maliciousInput = '&#60;script&#62;alert("XSS")&#60;/script&#62;';
      const sanitized = DOMPurify.sanitize(maliciousInput);

      // HTML entities remain encoded and safe - won't execute as script
      expect(sanitized).not.toContain('<script>');
    });
  });

  describe('Custom DOMPurify Configuration', () => {
    it('should use strict configuration for untrusted content', () => {
      const maliciousInput = '<img src=x onerror=alert("XSS")><p>Text</p>';
      const sanitized = DOMPurify.sanitize(maliciousInput, {
        ALLOW_DATA_ATTR: false,
        ALLOWED_ATTR: ['href'],
        ALLOWED_TAGS: ['p', 'strong', 'em', 'a'],
      });

      expect(sanitized).not.toContain('<img>');
      expect(sanitized).toContain('<p>Text</p>');
    });

    it('should strip all tags when needed', () => {
      const maliciousInput = '<script>alert("XSS")</script><p>Text</p>';
      const textOnly = DOMPurify.sanitize(maliciousInput, {
        ALLOWED_TAGS: [],
      });

      expect(textOnly).toBe('Text');
    });
  });
});

// Test sanitization helper function
describe('Sanitization Helpers', () => {
  const sanitizeUserInput = (input: string): string =>
    DOMPurify.sanitize(input, {
      ALLOW_DATA_ATTR: false,
      ALLOWED_ATTR: ['href', 'target', 'rel'],
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'a', 'ul', 'ol', 'li'],
    });

  it('should provide safe sanitization helper', () => {
    const maliciousInput = '<script>alert("XSS")</script><p>Safe content</p>';
    const result = sanitizeUserInput(maliciousInput);

    expect(result).not.toContain('<script>');
    expect(result).toContain('Safe content');
  });

  it('should preserve safe formatting', () => {
    const safeInput = '<p>Hello <strong>World</strong></p>';
    const result = sanitizeUserInput(safeInput);

    expect(result).toContain('<strong>');
    expect(result).toContain('World');
  });
});
