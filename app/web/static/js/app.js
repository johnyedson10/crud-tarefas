document.addEventListener("DOMContentLoaded", () => {
  const search = document.getElementById("task-search");
  const rows = document.querySelectorAll("#task-table tr");
  const forms = document.querySelectorAll("[data-api-form]");
  const table = document.getElementById("task-table");

  if (search && rows.length) {
    search.addEventListener("input", () => {
      const term = search.value.trim().toLowerCase();
      rows.forEach((row) => {
        const text = row.dataset.task?.toLowerCase() ?? "";
        row.style.display = text.includes(term) ? "" : "none";
      });
    });
  }

  forms.forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const response = await fetch(form.action, {
        method: form.method || "POST",
        body: new FormData(form),
        headers: { "X-Requested-With": "fetch" },
      });
      const data = await response.json();

      if (!response.ok || !data.ok) {
        alert(data.message || "Não foi possível concluir a ação.");
        return;
      }

      if (form.dataset.apiForm === "login" || form.dataset.apiForm === "register") {
        window.location.href = "/dashboard";
        return;
      }

      if (form.dataset.apiForm === "logout") {
        window.location.href = "/login";
        return;
      }

      if (form.dataset.apiForm === "task-create") {
        alert(data.message || "Tarefa cadastrada com sucesso.");
        window.location.reload();
        return;
      }

      window.location.reload();
    });
  });

  if (table) {
    table.addEventListener("click", async (event) => {
      const editButton = event.target.closest(".js-edit-task");
      const deleteButton = event.target.closest(".js-delete-task");
      const row = event.target.closest("tr");

      if (!row) {
        return;
      }

      if (editButton) {
        const id = row.dataset.taskId;
        const description = window.prompt("Descrição da tarefa:", row.dataset.taskDescription || "");
        if (description === null) {
          return;
        }
        const taskDatetime = window.prompt("Data e hora (YYYY-MM-DDTHH:MM):", row.dataset.taskDatetime || "");
        if (taskDatetime === null) {
          return;
        }
        const status = window.prompt("Status (Pendente, Em andamento, Concluída):", row.dataset.taskStatus || "Pendente");
        if (status === null) {
          return;
        }

        const response = await fetch(`/api/tasks/${id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ description, task_datetime: taskDatetime, status }),
        });
        const data = await response.json();

        if (!response.ok || !data.ok) {
          alert(data.message || "Não foi possível editar a tarefa.");
          return;
        }

        alert(data.message || "Tarefa atualizada com sucesso.");
        window.location.reload();
      }

      if (deleteButton) {
        const id = row.dataset.taskId;
        const confirmed = window.confirm("Deseja excluir esta tarefa?");
        if (!confirmed) {
          return;
        }

        const response = await fetch(`/api/tasks/${id}`, { method: "DELETE" });
        const data = await response.json();

        if (!response.ok || !data.ok) {
          alert(data.message || "Não foi possível excluir a tarefa.");
          return;
        }

        alert(data.message || "Tarefa excluída com sucesso.");
        window.location.reload();
      }
    });
  }
});
