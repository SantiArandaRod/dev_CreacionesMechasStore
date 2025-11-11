document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modalOverlayCliente");
  const abrirBtn = document.getElementById("abrirModalCliente");
  const cerrarBtn = document.getElementById("cerrarModalCliente");
  const form = document.getElementById("formCliente");
  const clientesBody = document.getElementById("clientesBody");

  // Abrir modal
  abrirBtn.addEventListener("click", () => modal.style.display = "flex");

  // Cerrar modal
  cerrarBtn.addEventListener("click", () => {
    modal.style.display = "none";
    form.reset();
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
      form.reset();
    }
  });

  // Enviar formulario para crear cliente
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const body = new URLSearchParams(formData);

    try {
      const res = await fetch("/clientes/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body
      });
      if (res.ok) {
        alert("✅ Cliente agregado");
        modal.style.display = "none";
        form.reset();
        cargarClientes();
      } else {
        const data = await res.json();
        alert("⚠️ " + (data.detail || JSON.stringify(data)));
      }
    } catch (err) {
      console.error(err);
      alert("❌ Error de conexión");
    }
  });

  // Inactivar o recuperar cliente
  clientesBody.addEventListener("click", async (e) => {
    if (e.target.matches(".btn-inactivar") || e.target.matches(".btn-recuperar")) {
      const id = e.target.getAttribute("data-id");

      // DEBUG: Verificar que el ID existe
      console.log("ID capturado:", id);

      if (!id || id === "undefined" || id === "null") {
        alert("❌ Error: ID de cliente no válido");
        console.error("Botón sin data-id válido:", e.target);
        return;
      }

      const action = e.target.matches(".btn-inactivar") ? "inactivar" : "recuperar";

      try {
        const res = await fetch(`/clientes/${id}/${action}`, { method: "POST" });
        if (res.ok) {
          cargarClientes();
        } else {
          const data = await res.json();
          alert("⚠️ " + (data.detail || JSON.stringify(data)));
        }
      } catch (err) {
        console.error(err);
        alert("❌ Error de conexión");
      }
    }
  });

  async function cargarClientes() {
    try {
      const res = await fetch("/clientes/");
      if (!res.ok) throw await res.json();
      const data = await res.json();

      // DEBUG: Verificar estructura de datos
      console.log("Datos recibidos:", data);

      renderClientes(data.clientes);
    } catch (err) {
      console.error(err);
      alert("❌ Error cargando clientes");
    }
  }

  function renderClientes(clientes) {
    clientesBody.innerHTML = "";
    if (!clientes || clientes.length === 0) {
      clientesBody.innerHTML = `<tr><td colspan="5" style="text-align:center">No hay clientes</td></tr>`;
      return;
    }

    clientes.forEach(c => {
      // DEBUG: Verificar que cada cliente tiene ID
      if (!c.id) {
        console.error("Cliente sin ID:", c);
      }

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${c.nombre || 'N/A'}</td>
        <td>${c.telefono || 'N/A'}</td>
        <td>${c.email || 'N/A'}</td>
        <td>${c.activo ? "Activo" : "Inactivo"}</td>
        <td>
          ${c.activo
            ? `<button class="btn-inactivar" data-id="${c.id}">Inactivar</button>`
            : `<button class="btn-recuperar" data-id="${c.id}">Recuperar</button>`}
        </td>`;
      clientesBody.appendChild(tr);
    });
  }

  // Cargar inicialmente
  cargarClientes();
});