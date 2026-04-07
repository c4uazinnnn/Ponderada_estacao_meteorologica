function initChart() {
  const canvas = document.getElementById("leiturasChart");
  const scriptData = document.getElementById("leituras-data");

  if (!canvas || !scriptData || typeof Chart === "undefined") {
    return;
  }

  let leituras = [];
  try {
    leituras = JSON.parse(scriptData.textContent || "[]");
  } catch (error) {
    console.error("Falha ao ler dados do grafico:", error);
    return;
  }

  const labels = leituras.map((item) => item.data_hora);
  const temperaturas = leituras.map((item) => item.temperatura);
  const umidades = leituras.map((item) => item.umidade);

  new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Temperatura (C)",
          data: temperaturas,
          borderColor: "#e76f51",
          backgroundColor: "rgba(231, 111, 81, 0.2)",
          tension: 0.25,
        },
        {
          label: "Umidade (%)",
          data: umidades,
          borderColor: "#2a9d8f",
          backgroundColor: "rgba(42, 157, 143, 0.2)",
          tension: 0.25,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: "top",
        },
      },
    },
  });
}

function initDeleteButtons() {
  const deleteButtons = document.querySelectorAll(".delete-btn");
  if (!deleteButtons.length) {
    return;
  }

  deleteButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      const id = button.dataset.id;
      if (!id) {
        return;
      }

      const confirmed = window.confirm(`Deseja realmente excluir a leitura ${id}?`);
      if (!confirmed) {
        return;
      }

      try {
        const response = await fetch(`/leituras/${id}?formato=json`, {
          method: "DELETE",
        });
        if (!response.ok) {
          throw new Error("Erro ao excluir leitura");
        }
        window.location.reload();
      } catch (error) {
        alert("Nao foi possivel excluir a leitura.");
      }
    });
  });
}

function initEditForm() {
  const form = document.getElementById("editar-form");
  if (!form) {
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const id = form.dataset.id;
    if (!id) {
      return;
    }

    const payload = {
      temperatura: Number(document.getElementById("temperatura").value),
      umidade: Number(document.getElementById("umidade").value),
      pressao: Number(document.getElementById("pressao").value),
    };

    try {
      const response = await fetch(`/leituras/${id}?formato=json`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Erro ao atualizar leitura");
      }

      window.location.href = "/leituras";
    } catch (error) {
      alert("Nao foi possivel atualizar a leitura.");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initChart();
  initDeleteButtons();
  initEditForm();
});
