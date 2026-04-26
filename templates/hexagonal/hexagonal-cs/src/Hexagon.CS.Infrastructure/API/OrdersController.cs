using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Hexagon.CS.Application.UseCases;

namespace Hexagon.CS.Infrastructure.API;

[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{
    private readonly CreateOrderUseCase _createOrderUseCase;

    public OrdersController(CreateOrderUseCase createOrderUseCase)
    {
        _createOrderUseCase = createOrderUseCase;
    }

    /// <summary>
    /// HTTP API adapter - exposes use cases via REST endpoints
    /// Receives HTTP requests → Calls application layer → Returns HTTP responses
    /// </summary>
    [HttpPost]
    public async Task<IActionResult> CreateOrder([FromBody] CreateOrderRequest request)
    {
        try
        {
            var result = await _createOrderUseCase.ExecuteAsync(request);
            return Ok(result);
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { error = ex.Message });
        }
    }
}
