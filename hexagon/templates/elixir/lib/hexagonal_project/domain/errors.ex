defmodule HexagonalProject.Domain.Errors do
  @moduledoc """
  Domain error definitions.
  """

  defmodule DomainError do
    @moduledoc """
    Base domain error.
    """
    defexception [:message, :code]

    @type t :: %__MODULE__{
            message: String.t(),
            code: atom()
          }

    def exception(message: message, code: code) do
      %__MODULE__{message: message, code: code}
    end
  end

  defmodule NotFoundError do
    @moduledoc """
    Entity not found error.
    """
    defexception [:message, :code]

    @type t :: %__MODULE__{
            message: String.t(),
            code: atom()
          }

    def exception(message: message) do
      %__MODULE__{message: message, code: :not_found}
    end
  end

  defmodule ValidationError do
    @moduledoc """
    Validation error.
    """
    defexception [:message, :code, :field]

    @type t :: %__MODULE__{
            message: String.t(),
            code: atom(),
            field: atom()
          }

    def exception(message: message, field: field) do
      %__MODULE__{message: message, code: :validation_error, field: field}
    end
  end

  defmodule BusinessRuleError do
    @moduledoc """
    Business rule violation error.
    """
    defexception [:message, :code]

    @type t :: %__MODULE__{
            message: String.t(),
            code: atom()
          }

    def exception(message: message) do
      %__MODULE__{message: message, code: :rule_violation}
    end
  end
end
