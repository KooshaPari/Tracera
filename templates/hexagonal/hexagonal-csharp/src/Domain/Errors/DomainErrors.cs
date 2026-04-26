namespace HexagonalCSharp.Domain.Errors;

/// <summary>
/// Base class for all domain errors.
/// </summary>
public abstract class DomainException : Exception
{
    public string Code { get; }
    public IReadOnlyDictionary<string, object?> Context { get; }

    protected DomainException(string message, string code, IReadOnlyDictionary<string, object?>? context = null)
        : base(message)
    {
        Code = code;
        Context = context ?? new Dictionary<string, object?>();
    }

    public virtual IDictionary<string, object?> ToDictionary() =>
        new Dictionary<string, object?>
        {
            ["code"] = Code,
            ["message"] = Message,
            ["context"] = Context.ToDictionary(kvp => kvp.Key, kvp => kvp.Value)
        };
}

/// <summary>
/// Thrown when an entity cannot be found.
/// </summary>
public class EntityNotFoundException : DomainException
{
    public string EntityType { get; }
    public string EntityId { get; }

    public EntityNotFoundException(string entityType, string entityId)
        : base(
            $"{entityType} with id '{entityId}' not found",
            "ENTITY_NOT_FOUND",
            new Dictionary<string, object?> { ["entityType"] = entityType, ["entityId"] = entityId }
        )
    {
        EntityType = entityType;
        EntityId = entityId;
    }
}

/// <summary>
/// Thrown when a business rule is violated.
/// </summary>
public class BusinessRuleViolationException : DomainException
{
    public string Rule { get; }
    public string Details { get; }

    public BusinessRuleViolationException(string rule, string details)
        : base(
            $"Business rule violated: {rule}",
            "BUSINESS_RULE_VIOLATION",
            new Dictionary<string, object?> { ["rule"] = rule, ["details"] = details }
        )
    {
        Rule = rule;
        Details = details;
    }
}

/// <summary>
/// Thrown when validation fails.
/// </summary>
public class ValidationException : DomainException
{
    public string Field { get; }
    public object? Value { get; }
    public string Constraint { get; }

    public ValidationException(string field, object? value, string constraint)
        : base(
            $"Validation failed for field '{field}'",
            "VALIDATION_ERROR",
            new Dictionary<string, object?> { ["field"] = field, ["value"] = value, ["constraint"] = constraint }
        )
    {
        Field = field;
        Value = value;
        Constraint = constraint;
    }
}

/// <summary>
/// Thrown when an invalid state transition is attempted.
/// </summary>
public class InvalidStateTransitionException : DomainException
{
    public string EntityType { get; }
    public string CurrentState { get; }
    public string AttemptedState { get; }

    public InvalidStateTransitionException(string entityType, string currentState, string attemptedState)
        : base(
            $"Invalid state transition for {entityType}: {currentState} -> {attemptedState}",
            "INVALID_STATE_TRANSITION",
            new Dictionary<string, object?>
            {
                ["entityType"] = entityType,
                ["currentState"] = currentState,
                ["attemptedState"] = attemptedState
            }
        )
    {
        EntityType = entityType;
        CurrentState = currentState;
        AttemptedState = attemptedState;
    }
}
