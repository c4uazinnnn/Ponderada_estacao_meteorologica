function initChart() {
  const temperaturaCanvas = document.getElementById("temperaturaChart");
  const umidadeCanvas = document.getElementById("umidadeChart");
  const pressaoCanvas = document.getElementById("pressaoChart");
  const scriptData = document.getElementById("leituras-data");

  if (!temperaturaCanvas || !umidadeCanvas || !pressaoCanvas || !scriptData || typeof Chart === "undefined") {
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
  const temperaturas = leituras.map((item) => Number(item.temperatura));
  const umidades = leituras.map((item) => Number(item.umidade));
  const pressoes = leituras.map((item) => Number(item.pressao));

  function calcularEscalaReal(valores) {
    const numeros = valores.map((v) => Number(v)).filter((v) => Number.isFinite(v));
    if (!numeros.length) {
      return {};
    }

    let min = Math.min(...numeros);
    let max = Math.max(...numeros);

    if (min === max) {
      const margem = Math.max(Math.abs(min) * 0.1, 1);
      min -= margem;
      max += margem;
    }

    const range = max - min;
    const alvoTicks = 6;
    const passoBruto = range / alvoTicks;
    const magnitude = Math.pow(10, Math.floor(Math.log10(passoBruto)));
    const normalizado = passoBruto / magnitude;

    let fator;
    if (normalizado <= 1) {
      fator = 1;
    } else if (normalizado <= 2) {
      fator = 2;
    } else if (normalizado <= 5) {
      fator = 5;
    } else {
      fator = 10;
    }

    const stepSize = fator * magnitude;
    const yMin = Math.floor(min / stepSize) * stepSize;
    const yMax = Math.ceil(max / stepSize) * stepSize;

    return {
      min: yMin,
      max: yMax,
      ticks: {
        stepSize,
        padding: 8,
      },
    };
  }

  function criarOpcoes(yScale) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: {
          top: 8,
          right: 8,
          bottom: 4,
          left: 8,
        },
      },
      plugins: {
        legend: {
          position: "top",
        },
      },
      scales: {
        x: {
          ticks: {
            autoSkip: true,
            maxTicksLimit: 5,
            maxRotation: 0,
            padding: 8,
          },
        },
        y: yScale,
      },
    };
  }

  const escalaTemperatura = calcularEscalaReal(temperaturas);
  const escalaUmidade = calcularEscalaReal(umidades);
  const escalaPressao = calcularEscalaReal(pressoes);

  new Chart(temperaturaCanvas, {
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
      ],
    },
    options: criarOpcoes(escalaTemperatura),
  });

  new Chart(umidadeCanvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Umidade (%)",
          data: umidades,
          borderColor: "#2a9d8f",
          backgroundColor: "rgba(42, 157, 143, 0.2)",
          tension: 0.25,
        },
      ],
    },
    options: criarOpcoes(escalaUmidade),
  });

  new Chart(pressaoCanvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Pressao (hPa)",
          data: pressoes,
          borderColor: "#264653",
          backgroundColor: "rgba(38, 70, 83, 0.2)",
          tension: 0.25,
        },
      ],
    },
    options: criarOpcoes(escalaPressao),
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

function initRefreshButton() {
  const refreshButton = document.getElementById("refresh-history") || document.getElementById("refresh-home");
  if (!refreshButton) {
    return;
  }

  refreshButton.addEventListener("click", () => {
    window.location.reload();
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
  initRefreshButton();
  initDeleteButtons();
  initEditForm();
});
