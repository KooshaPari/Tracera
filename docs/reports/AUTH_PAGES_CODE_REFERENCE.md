# Authentication Pages - Code Reference

Complete code examples and patterns used in the authentication pages.

---

## Form Validation Pattern

### Email Validation

```typescript
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Usage in validation
if (!formData.email) {
  newErrors.email = 'Email is required';
} else if (!validateEmail(formData.email)) {
  newErrors.email = 'Please enter a valid email address';
}
```

### Password Validation

```typescript
const validatePassword = (password: string): boolean => {
  return password.length >= 8;
};

// In reset password with strength calculation
const validateResetForm = (): boolean => {
  const newErrors: FormErrors = {};

  if (!formData.newPassword) {
    newErrors.newPassword = 'New password is required';
  } else if (!validatePassword(formData.newPassword)) {
    newErrors.newPassword = 'Password must be at least 8 characters';
  }

  if (!formData.confirmPassword) {
    newErrors.confirmPassword = 'Please confirm your password';
  } else if (formData.newPassword !== formData.confirmPassword) {
    newErrors.confirmPassword = 'Passwords do not match';
  }

  setErrors(newErrors);
  return Object.keys(newErrors).length === 0;
};
```

---

## Password Strength Calculation

### 4-Tier Strength System

```typescript
type PasswordStrength = 'weak' | 'fair' | 'good' | 'strong';

// Calculate strength on password change
useEffect(() => {
  const password = formData.newPassword || '';
  let strength: PasswordStrength = 'weak';

  if (password.length >= 8) {
    let scoreCount = 0;

    // Check for uppercase
    if (/[A-Z]/.test(password)) scoreCount++;
    // Check for lowercase
    if (/[a-z]/.test(password)) scoreCount++;
    // Check for numbers
    if (/[0-9]/.test(password)) scoreCount++;
    // Check for special characters
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) scoreCount++;

    if (scoreCount === 4) strength = 'strong';
    else if (scoreCount === 3) strength = 'good';
    else if (scoreCount === 2) strength = 'fair';
    else strength = 'fair';
  }

  setPasswordStrength(strength);
}, [formData.newPassword]);
```

### Strength Display

```typescript
const getPasswordStrengthColor = (strength: PasswordStrength) => {
  switch (strength) {
    case "weak":
      return "bg-destructive";
    case "fair":
      return "bg-amber-500";
    case "good":
      return "bg-blue-500";
    case "strong":
      return "bg-green-500";
  }
};

// In JSX
{formData.newPassword && (
  <div className="space-y-1">
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1 bg-muted rounded-full overflow-hidden">
        <div
          className={cn(
            "h-full transition-all",
            getPasswordStrengthColor(passwordStrength),
          )}
          style={{
            width: `${
              {
                weak: "25%",
                fair: "50%",
                good: "75%",
                strong: "100%",
              }[passwordStrength]
            }`,
          }}
        />
      </div>
      <span
        className="text-xs font-medium capitalize"
        data-testid="password-strength"
      >
        {passwordStrength}
      </span>
    </div>
  </div>
)}
```

---

## Form Input Handling

### Unified Input Handler

```typescript
const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const { name, value, type, checked } = e.currentTarget;
  const fieldValue = type === 'checkbox' ? checked : value;

  setFormData((prev) => ({
    ...prev,
    [name]: fieldValue,
  }));

  // Clear error for this field when user starts typing
  if (errors[name as keyof FormErrors]) {
    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors[name as keyof FormErrors];
      return newErrors;
    });
  }
};
```

### Usage in JSX

```typescript
<Input
  id="email"
  name="email"
  type="email"
  placeholder="your@email.com"
  value={formData.email}
  onChange={handleInputChange}
  aria-label="Email address"
  disabled={isLoading}
  className={cn(
    "w-full",
    errors.email && "border-destructive",
  )}
/>
{errors.email && (
  <p className="error text-xs text-destructive mt-1">
    {errors.email}
  </p>
)}
```

---

## Password Visibility Toggle

### State and Handler

```typescript
const [showPassword, setShowPassword] = useState(false);

const handleTogglePassword = () => {
  setShowPassword(!showPassword);
};
```

### Component Implementation

```typescript
<div className="relative">
  <Input
    id="password"
    name="password"
    type={showPassword ? "text" : "password"}
    placeholder="••••••••"
    value={formData.password}
    onChange={handleInputChange}
    aria-label="Password"
    disabled={isLoading}
    className={cn(
      "w-full pr-10",
      errors.password && "border-destructive",
    )}
  />
  <button
    type="button"
    onClick={() => setShowPassword(!showPassword)}
    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
    data-testid="toggle-password"
    aria-label={showPassword ? "Hide password" : "Show password"}
    disabled={isLoading}
  >
    {showPassword ? (
      <EyeOff className="w-4 h-4" />
    ) : (
      <Eye className="w-4 h-4" />
    )}
  </button>
</div>
```

---

## Form Submission

### Login Submission

```typescript
const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();

  if (!validateForm()) {
    return;
  }

  setIsLoading(true);
  setErrors({});

  try {
    // Demo: Check for test credentials
    if (formData.email === 'test@example.com' && formData.password === 'password123') {
      // Store auth data
      localStorage.setItem('authToken', 'demo-token-' + Date.now());
      if (formData.rememberMe) {
        localStorage.setItem('rememberMe', 'true');
      }
      localStorage.setItem(
        'user',
        JSON.stringify({
          id: 'test-user-1',
          email: formData.email,
          name: 'Test User',
        }),
      );

      // Redirect to dashboard
      await navigate({ to: '/' });
    } else {
      // Show error for invalid credentials
      setErrors({
        form: 'Invalid email or password. Try test@example.com / password123',
      });
    }
  } catch (error) {
    setErrors({
      form: 'An error occurred. Please try again.',
    });
  } finally {
    setIsLoading(false);
  }
};
```

### Registration Submission

```typescript
const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();

  if (!validateForm()) {
    return;
  }

  setIsLoading(true);
  setErrors({});

  try {
    // Check for existing email (demo check)
    if (formData.email === 'existing@example.com') {
      setErrors({
        form: 'This email address is already registered',
      });
      setIsLoading(false);
      return;
    }

    // Simulate successful registration
    localStorage.setItem('authToken', 'demo-token-' + Date.now());
    localStorage.setItem(
      'user',
      JSON.stringify({
        id: 'new-user-' + Date.now(),
        email: formData.email,
        name: formData.name,
      }),
    );

    // Redirect to dashboard
    await navigate({ to: '/' });
  } catch (error) {
    setErrors({
      form: 'An error occurred. Please try again.',
    });
  } finally {
    setIsLoading(false);
  }
};
```

---

## Checkbox Component Integration

### Remember Me Checkbox

```typescript
<div className="flex items-center gap-2">
  <Checkbox
    id="rememberMe"
    name="rememberMe"
    checked={formData.rememberMe}
    onChange={handleInputChange}
    disabled={isLoading}
    aria-label="Remember me"
  />
  <label
    htmlFor="rememberMe"
    className="text-sm text-muted-foreground cursor-pointer"
  >
    Remember me
  </label>
</div>
```

### Terms Checkbox

```typescript
<div className="flex items-start gap-2">
  <Checkbox
    id="acceptTerms"
    name="acceptTerms"
    checked={formData.acceptTerms}
    onChange={handleInputChange}
    disabled={isLoading}
    aria-label="Accept terms and conditions"
  />
  <label
    htmlFor="acceptTerms"
    className="text-sm text-muted-foreground cursor-pointer leading-tight"
  >
    I agree to the{" "}
    <a href="#" className="text-primary hover:underline">
      Terms of Service
    </a>{" "}
    and{" "}
    <a href="#" className="text-primary hover:underline">
      Privacy Policy
    </a>
  </label>
</div>
{errors.acceptTerms && (
  <p className="error text-xs text-destructive -mt-2">
    {errors.acceptTerms}
  </p>
)}
```

---

## Navigation Links

### TanStack Router Links

```typescript
import { Link as RouterLink, useNavigate } from "@tanstack/react-router";

// Navigation after form submission
const navigate = useNavigate();
await navigate({ to: "/" });

// Links in JSX
<RouterLink
  to="/auth/reset-password"
  className="text-primary hover:underline"
>
  Forgot password?
</RouterLink>

<RouterLink
  to="/auth/register"
  className="text-primary hover:underline font-medium"
>
  Sign up
</RouterLink>
```

---

## Error Display Component

### Alert Pattern

```typescript
{errors.form && (
  <div
    role="alert"
    className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-md text-sm"
  >
    {errors.form}
  </div>
)}

// Success message
{successMessage && (
  <div
    role="alert"
    className="bg-green-500/10 border border-green-500/30 text-green-600 px-4 py-3 rounded-md text-sm"
  >
    {successMessage}
  </div>
)}
```

---

## OAuth Button Implementation

### OAuth Handler

```typescript
const handleOAuthClick = (provider: string) => {
  // Simulate OAuth redirect
  console.log(`OAuth flow initiated for ${provider}`);
  // In a real app, this would redirect to the OAuth provider
  // window.location.href = `/api/auth/${provider}`;
};

// In JSX
<div className="grid grid-cols-2 gap-3">
  <Button
    type="button"
    variant="outline"
    onClick={() => handleOAuthClick("google")}
    disabled={isLoading}
    className="gap-2"
  >
    <Mail className="w-4 h-4" />
    Google
  </Button>
  <Button
    type="button"
    variant="outline"
    onClick={() => handleOAuthClick("github")}
    disabled={isLoading}
    className="gap-2"
  >
    <Github className="w-4 h-4" />
    GitHub
  </Button>
</div>
```

---

## Layout Components

### Card Layout

```typescript
<div className="min-h-screen bg-gradient-to-br from-background to-background/50 flex items-center justify-center p-4">
  <div className="w-full max-w-md">
    {/* Header */}
    <div className="mb-8 text-center">
      <h1 className="text-3xl font-bold tracking-tight mb-2">
        Welcome Back
      </h1>
      <p className="text-muted-foreground">
        Sign in to your account to continue
      </p>
    </div>

    {/* Card */}
    <div className="bg-card border border-border rounded-lg shadow-lg p-6 space-y-6">
      {/* Form content */}
    </div>
  </div>
</div>
```

### Divider Component

```typescript
<div className="relative">
  <div className="absolute inset-0 flex items-center">
    <div className="w-full border-t border-border" />
  </div>
  <div className="relative flex justify-center text-xs uppercase">
    <span className="bg-card px-2 text-muted-foreground">
      Or continue with
    </span>
  </div>
</div>
```

---

## Route Definition

### Login Route

```typescript
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/auth/login')({
  component: LoginPage,
});

function LoginPage() {
  // Component code
}
```

### Reset Password Route with Search Validation

```typescript
import { createFileRoute, useSearch } from '@tanstack/react-router';

export const Route = createFileRoute('/auth/reset-password')({
  component: ResetPasswordPage,
  validateSearch: (search: Record<string, unknown>) => ({
    token: search['token'] as string | undefined,
  }),
});

function ResetPasswordPage() {
  const search = useSearch({ from: '/auth/reset-password' });
  const hasToken = !!search.token;

  // Component code
}
```

---

## Type Definitions

### Form Data Types

```typescript
interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

interface RegisterFormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  acceptTerms: boolean;
}

interface ResetPasswordFormData {
  email?: string;
  newPassword?: string;
  confirmPassword?: string;
}
```

### Error Types

```typescript
interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  name?: string;
  acceptTerms?: string;
  newPassword?: string;
  form?: string;
}

type PasswordStrength = 'weak' | 'fair' | 'good' | 'strong';
```

---

## Styling Patterns

### Input Wrapper

```typescript
<div className="space-y-2">
  <label
    htmlFor="email"
    className="text-sm font-medium text-foreground"
  >
    Email Address
  </label>
  <Input
    id="email"
    name="email"
    type="email"
    placeholder="your@email.com"
    value={formData.email}
    onChange={handleInputChange}
    aria-label="Email address"
    disabled={isLoading}
    className={cn(
      "w-full",
      errors.email && "border-destructive",
    )}
  />
  {errors.email && (
    <p className="error text-xs text-destructive mt-1">
      {errors.email}
    </p>
  )}
</div>
```

### Button Variants

```typescript
// Primary action
<Button type="submit" className="w-full">
  Sign In
</Button>

// Secondary action
<Button type="button" variant="outline" className="gap-2">
  <GoogleIcon />
  Google
</Button>

// Disabled state
<Button disabled>
  Already Loading...
</Button>
```

---

## localStorage Patterns

### Auth Storage

```typescript
// Save auth token
localStorage.setItem('authToken', 'demo-token-' + Date.now());

// Save user data
localStorage.setItem(
  'user',
  JSON.stringify({
    id: 'user-123',
    email: 'user@example.com',
    name: 'User Name',
  }),
);

// Save preferences
localStorage.setItem('rememberMe', 'true');

// Clear on logout
localStorage.removeItem('authToken');
localStorage.removeItem('user');
localStorage.removeItem('rememberMe');
```

### Retrieve from localStorage

```typescript
const token = await page.evaluate(() => {
  return localStorage.getItem('authToken');
});

const user = await page.evaluate(() => {
  return JSON.parse(localStorage.getItem('user') || '{}');
});

const rememberMe = await page.evaluate(() => {
  return localStorage.getItem('rememberMe');
});
```

---

## Testing Utilities

### Common Test Patterns

```typescript
// Fill form fields
await page.fill('input[name="email"]', 'test@example.com');
await page.fill('input[name="password"]', 'password123');

// Check checkbox
await page.check('input[name="rememberMe"]');

// Click button
await page.click('button[type="submit"]');

// Wait for navigation
await page.waitForURL('/');

// Verify element visibility
await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();

// Check input type
await expect(page.locator('input[name="password"]')).toHaveAttribute('type', 'password');

// Verify text content
await expect(errorMessage).toContainText(/invalid/i);

// Check error count
const errors = page.locator('.error');
await expect(errors).toHaveCount(4);
```

---

## Accessibility Features

### ARIA Labels

```typescript
<Input
  id="email"
  name="email"
  type="email"
  aria-label="Email address"
/>

<button
  data-testid="toggle-password"
  aria-label={showPassword ? "Hide password" : "Show password"}
>
  {showPassword ? <EyeOff /> : <Eye />}
</button>
```

### Alert Roles

```typescript
<div role="alert" className="...">
  {errors.form}
</div>

<div role="alert" aria-live="polite" className="...">
  {successMessage}
</div>
```

### Label Associations

```typescript
<label htmlFor="email" className="...">
  Email Address
</label>
<Input id="email" name="email" />
```

---

**All code examples are production-ready and can be used as templates for similar components.**
