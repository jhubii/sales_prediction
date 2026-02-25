using System.Collections.Concurrent;
using System.Linq;
using System.Threading;
using Microsoft.AspNetCore.Mvc;
using web_app.Models;

namespace web_app.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TodoItemsController : ControllerBase
{
    private static readonly ConcurrentDictionary<int, TodoItem> Store = new();
    private static int _nextId = 0;

    [HttpGet]
    public ActionResult<IEnumerable<TodoItem>> GetAll()
    {
        return Ok(Store.Values.OrderBy(item => item.Id));
    }

    [HttpGet("{id:int}")]
    public ActionResult<TodoItem> GetById(int id)
    {
        if (!Store.TryGetValue(id, out var item))
        {
            return NotFound();
        }

        return Ok(item);
    }

    [HttpPost]
    public ActionResult<TodoItem> Create([FromBody] TodoItem input)
    {
        if (string.IsNullOrWhiteSpace(input.Title))
        {
            return BadRequest("Title is required.");
        }

        var id = Interlocked.Increment(ref _nextId);
        var item = new TodoItem
        {
            Id = id,
            Title = input.Title.Trim(),
            IsComplete = input.IsComplete
        };

        Store[id] = item;

        return CreatedAtAction(nameof(GetById), new { id }, item);
    }

    [HttpPut("{id:int}")]
    public ActionResult<TodoItem> Update(int id, [FromBody] TodoItem input)
    {
        if (!Store.ContainsKey(id))
        {
            return NotFound();
        }

        if (string.IsNullOrWhiteSpace(input.Title))
        {
            return BadRequest("Title is required.");
        }

        var updated = new TodoItem
        {
            Id = id,
            Title = input.Title.Trim(),
            IsComplete = input.IsComplete
        };

        Store[id] = updated;

        return Ok(updated);
    }

    [HttpDelete("{id:int}")]
    public IActionResult Delete(int id)
    {
        if (!Store.TryRemove(id, out _))
        {
            return NotFound();
        }

        return NoContent();
    }
}
