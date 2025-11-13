document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("modalOverlayCliente");
  const form = document.getElementById("formCliente");
  const abrirModal = document.getElementById("abrirModalCliente");
  const cerrarModal = document.getElementById("cerrarModalCliente");
  const clientesBody = document.getElementById("clientesBody");

  let modoEdicion = false;
  let clienteEditandoId = null;

  // === Abrir modal (para nuevo cliente) ===
  abrirModal.addEventListener("click", () => {
    modoEdicion = false;
    clienteEditandoId = null;
    form.reset();
    form.querySelector("h2")?.remove(); // limpiar si ya hay título previo
    const h2 = document.createElement("h2");
    h2.textContent = "Agregar Cliente";
    form.prepend(h2);
    overlay.style.display = "flex";
  });

  // === Cerrar modal ===
  cerrarModal.addEventListener("click", () => {
    overlay.style.display = "none";
    form.reset();
    modoEdicion = false;
    clienteEditandoId = null;
  });

  // === Cerrar modal clic fuera ===
  window.addEventListener("click", (e) => {
    if (e.target === overlay) {
      overlay.style.display = "none";
      form.reset();
      modoEdicion = false;
      clienteEditandoId = null;
    }
  });

  // === Enviar formulario (crear o editar) ===
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const data = new URLSearchParams({
      nombre: formData.get("nombre").trim(),
      telefono: formData.get("telefono").trim(),
      email: formData.get("email").trim().toLowerCase()
    });

    const url = modoEdicion
      ? `/clientes/${clienteEditandoId}`
      : "/clientes/";
    const method = modoEdicion ? "PUT" : "POST";

    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: data
      });

      if (res.ok) {
        alert(modoEdicion ? "✅ Cliente actualizado" : "✅ Cliente creado");
        overlay.style.display = "none";
        form.reset();
        modoEdicion = false;
        clienteEditandoId = null;
        cargarClientes();
      } else {
        const err = await res.json();
        alert("⚠️ " + (err.detail || "Error en la operación"));
      }
    } catch (error) {
      console.error(error);
      alert("❌ Error de conexión");
    }
  });

  // === Inactivar, Activar o Editar ===
  clientesBody.addEventListener("click", async (e) => {
    const btn = e.target;

    if (btn.classList.contains("btn-inactivar") || btn.classList.contains("btn-activar")) {
      const id = btn.dataset.id;
      const accion = btn.classList.contains("btn-inactivar") ? "inactivar" : "activar";

      try {
        const res = await fetch(`/clientes/${id}/${accion}`, { method: "POST" });
        if (res.ok) {
          cargarClientes();
        } else {
          const err = await res.json();
          alert("⚠️ " + (err.detail || "Error en el cambio de estado"));
        }
      } catch (error) {
        console.error(error);
        alert("❌ Error al conectar con el servidor");
      }
    }

    // === Editar cliente ===
    if (btn.classList.contains("btn-editar")) {
      const id = btn.dataset.id;
      try {
        const res = await fetch(`/clientes/${id}`);
        if (!res.ok) throw await res.json();
        const cliente = await res.json();

        // Rellenar modal
        modoEdicion = true;
        clienteEditandoId = cliente.id_cliente;
        form.querySelector("h2")?.remove();
        const h2 = document.createElement("h2");
        h2.textContent = "Editar Cliente";
        form.prepend(h2);

        form.nombre.value = cliente.nombre;
        form.telefono.value = cliente.telefono;
        form.email.value = cliente.email;

        overlay.style.display = "flex";
      } catch (error) {
        console.error(error);
        alert("❌ No se pudo cargar el cliente");
      }
    }
  });

  // === Cargar clientes ===
  async function cargarClientes() {
    try {
      const res = await fetch("/clientes/");
      if (!res.ok) throw await res.json();
      const data = await res.json();
      renderClientes(data.clientes);
    } catch (err) {
      console.error(err);
      alert("❌ Error al cargar los clientes");
    }
  }

  // === Renderizar tabla ===
  function renderClientes(clientes) {
    clientesBody.innerHTML = "";
    if (!clientes.length) {
      clientesBody.innerHTML = `<tr><td colspan="5" style="text-align:center">No hay clientes</td></tr>`;
      return;
    }

    clientes.forEach(c => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${c.nombre}</td>
        <td>${c.telefono}</td>
        <td>${c.email}</td>
        <td>${c.activo ? '<span style="color:green">Activo</span>' : '<span style="color:red">Inactivo</span>'}</td>
        <td>
          <button class="btn-editar" data-id="${c.id_cliente}">Editar</button>
          ${c.activo
            ? `<button class="btn-inactivar" data-id="${c.id_cliente}">Inactivar</button>`
            : `<button class="btn-activar" data-id="${c.id_cliente}">Activar</button>`}
        </td>
      `;
      clientesBody.appendChild(tr);
    });
  }

  cargarClientes();
});
