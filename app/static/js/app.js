// Minimal client for the JSON API. The token lives in sessionStorage and
// travels only in the Authorization header: the browser never attaches it
// on its own, the way it would with a cookie.

// se puede ver en DevTools -> Application -> Session Storage
const TOKEN_KEY = "access_token";

// función lambda = función flecha
// const: const en lugar de let para no cambiar la función por ejemplo
// $: popularizado por jQuery, funciona como una letra cualquiera, no tiene nada de especial
// (id): parámetros de la función flecha
// =>: define la función
// document.getElementById(id): se asigna a $ el valor que devuelva este cuerpo de la función
/*
es el equivalente a hacer:
function $(id) {
    return document.getElementById(id);
}
Es una convención muy común: function para lo importante, flechas para lo corto y para los callbacks.
*/
// document: es la puerta de entrada al DOM, DOM es el árbol de objetos que representa la página
const $ = (id) => document.getElementById(id);

// ---------------------------------------------------------------- token
function getToken() {
    return sessionStorage.getItem(TOKEN_KEY); // lee el valor de la clave TOKEN_KEY, es decir el token guardado
}

function setToken(token){
    if (token) sessionStorage.setItem(TOKEN_KEY, token); // guarda el valor token en la clave TOKEN_KEY
    else sessionStorage.removeItem(TOKEN_KEY); // borra el valor guardado en la clave TOKEN_KEY
}

// Read the payload to show who is signed in and when the token expires.
// This does NOT verify the signature: only the server can, and it does on
// every request.
// leer el payload sin verificar la firma
function payload() {
    const token = getToken();
    if (!token) return null;

    try {
        // un JWT se compone: header.payload.firma
        // el payload tiene el sub, username, exp, etc.
        const part = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"); // reemplaza + por - y / por _, para no tener problemas en la URL
        return JSON.parse(atob(part)); // atob: decodifica texto en Base64 (ASCII a binary)
    } catch {
        return null;
    }
}

// ---------------------------------------------------------------- API
// llamada a la API, devuelve el body de la respuesta
// api(): verifica la firma en cada petición y junto a render() limita la visualización de las páginas envolviendo cada petición fetch()
async function api(path, { method = "GET", body } = {}) {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`; // añade el header a la petición
    
    // contiene del body?
    // si no hay body, da undefined y no se envía body, si hay body se convierte a JSON
    // fetch(): devuelve un objeto Response
    // fetch no da error con un Status Code 400 o 500, la Promise se resuelve con normalidad
    // sino cuando no hubo respuesta:
    //      - el servidor está apagado
    //      - no hay red
    //      - un problema de CORS
    const res = await fetch(path, { method, headers, body: body && JSON.stringify(body) });
    
    // res.json() lee el body y lo convierte en objeto ¿JSON?
    // si el cuerpo no es JSON queda como {}
    // ({}): devuelve un objeto vacío ya que usar () => {} directamente sería interpretado como una función Lambda
    const data = await res.json().catch(() => ({}));

    if (res.status === 401 && token) {
        setToken(null); // expired or invalid: back to the login form
        void render();
    }

    // .ok: propiedad del objeto Response, da true si Status Code está entre 200-299 y false con cualquier otro (por ejemplo: 4xx, 5xx)
    // throw: lanza el error que vino del servidor y fue CATCHEADO en res.json.catch() al definir data=
    // este throw se CATCHEA en run()
    if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`); // data.message: son mensajes de error como "Invalid username or password", etc.

    return data;
}

// ---------------------------------------------------------------- views
function show(message, kind = "error") {
    const box = $("message");
    box.textContent = message;
    box.className = `flash flash-${kind}`;
    box.hidden = !message; // !message: da un booleando, False si está vacío y True si tiene contenido
}

// Run an async action and show its error, if any.
async function run(action) { // se pasa una función action sin ejecutarla (es decir sin paréntesis ())
    show("");

    // así no se repite un try/catch en cada botón
    try {
        await action(); // la función se ejecuta recién aquí
    } catch (err) {
        show(err.message);
    }
}

async function render() {
    const user = payload();
    // hay usuario y su token no se venció
    const signedIn = Boolean(user) && user.exp * 1000 > Date.now(); // now() está en milisegundos, el  * 1000 es para convertir user.exp a milisegundos y poder hacer la comparación
    if (!signedIn) setToken(null);

    $("auth-view").hidden = signedIn;
    $("todos-view").hidden = !signedIn; // muestra las tareas
    $("logout").hidden = !signedIn;
    $("who").textContent = signedIn ? user.username : "";

    if (signedIn) await loadTodos();
}

async function loadTodos() {
    const { todos } = await api("/api/todos"); // saca la variable concreta de todos (que es un array) de la respuesta de api()

    // los hijos en este caso es <li> de <ul>
    // replaceChildren(): borra los hijos anterior y pone los nuevos
    // ...: spred -> expande el array en argumento sueltos li1, li2, li3, etc
    // Todo.map(todoItem): llama a todoItem(todo) por cada tarea y devuelve un array de <li> 
    $("todo-list").replaceChildren(...todos.map(todoItem));
    $("count").textContent = `(${todos.length})`;
    $("empty").hidden = todos.length > 0; // > 0 -> hidden true -> el mensaje se oculta, = 0 -> hidden false -> se muestra "No todos yet"
}

// A button that calls the API and then reloads the list.
// If the action returns nothing (the user cancelled), nothing is reloaded.
function button(text, className, action) {
    // createElement(): solo crea el elemento en memoria, pero no agrega nada todavía, es decir que no se ve en la página
    const b = document.createElement("button");

    b.type = "button";
    b.className = className;
    b.textContent = text;

    // , (): es la función que le pases para que se ejecute cuando se hace click en el button
    // () => run(): esa función llama a run()
    // () => function(): es una función guardada, le dice: no lo hagas ahora, hazlo cuando te llamen
    // se hace con esta notación () => function(), por qué hace "click", run(), ejecutaría inmediatamente en run cuando se cree el button
    // async () => {}: es la función que recibe run()
    b.addEventListener("click", () => run(async () => {
        // si action() devolvio algo verdadero, entonces recarga la lista
        // action(): recién ejecuta aquí la función que se paso por parámetro
        if (await action()) await loadTodos();
    }));

    return b;
}

// Built with textContent, never innerHTML: a title such as
// <img src=x onerror=...> is shown as text instead of running.
function todoItem(todo) {
    const li = document.createElement("li");
    li.className = "todo-item" + (todo.completed ? " completed" : "");

    const check = button(todo.completed ? "✔" : "", "checkbox", () => 
        api(`/api/todos/${todo.id}`, { 
            method: "PATCH", 
            body: { completed: !todo.completed }
        })
    );
    check.setAttribute("aria-label", "Toggle completed"); 
    // toggle significa alternar como un switch (interruptor) para prender y apagar la luz
    // setAttribute(): pone un atributo HTML en el elemento, en este caso en check

    const body = document.createElement("div");
    body.className = "todo-body";

    const title = document.createElement("span");
    title.className = "todo-title";
    title.textContent = todo.title;
    body.append(title);

    if (todo.description) {
        const description = document.createElement("p");
        description.className = "todo-description";
        description.textContent = todo.description;
        body.append(description);
    }

    const actions = document.createElement("div");
    actions.className = "todo-actions";
    actions.append(button("Edit", "btn btn-small", () => {
        const newTitle = prompt("New title", todo.title); // prompt(mensaje, valor inicial del campo): abre una ventanita del navegador con un campo de texto
        return newTitle && api(`/api/todos/${todo.id}`, { // se guarda null en newTitle si en prompt se hace "Cancelar", entonces no se llama a la api
            method: "PATCH",
            body: { title: newTitle }
        });
    }));
    actions.append(button("Delete", "btn btn-small btn-danger", () => 
    confirm("Delete this todo?") && api(`/api/todos/${todo.id}`, { // confirm(mensaje): ventanita con el mensaje, si se presiona Aceptar:true, si es Cancelar:false
        method: "DELETE"
    })));

    li.append(check, body, actions);
    return li;
}

// ---------------------------------------------------------------- events
function credentials() {
    return { username: $("username").value, password: $("password").value };
}

async function signIn() {
    const { access_token } = await api("/auth/login", { method: "POST", body: credentials() }); // devuelve el token
    setToken(access_token);
    $("login-form").reset(); // reset(): devuelve los campos del form a su valor inicial ya que ya se inicio sesión
    await render();
}

$("login-form").addEventListener("submit", (event) => {
    event.preventDefault();
    void run(signIn);
});

$("register").addEventListener("click", () => run(async() => {
    if (!$("login-form").reportValidity()) return; // reportValidity(): fuerza required ya que Create account es un type=button y no un type=submit

    await api("/auth/register", { method: "POST", body: credentials() }); // no devuelve el token
    await signIn();

    show("Account created.", "success");
}));

$("create-form").addEventListener("submit", (event) => {
    event.preventDefault();
    // event.target = create-form = $("create-form")
    // event.target.elements = los campos de create-form, accesibles por su name
    const fields = event.target.elements; // event.target: es el elemento donde ocurrió el evento -> en este caso es el propio create-form

    // void para que SonarQube ignore la falta de await en el promise siendo que dentro de run() ya se hace eso
    void run(async () => {
        await api("/api/todos", {
            method: "POST",
            body: { title: fields.title.value, description: fields.description.value },
        });
        event.target.reset(); // reset(): limpia ese form -> create-form en este caso
        await loadTodos();
    });
});

$("logout").addEventListener("click", () => {
    setToken(null); // solo borra el token
    void render();
    show("Signed out.", "success");
});

/*
1. se ingresa a / -> las 2 vistas están ocultas
2. se ejecuta app.js -> nada visible aún hasta que...
3. run(render) -> se ejecuta async function render()
*/
void run(render);