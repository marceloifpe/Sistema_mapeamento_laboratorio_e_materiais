// Define o caminho do arquivo JSON contendo os eventos do calendário
let request_calendar = "./events.json"

// Obtém o elemento HTML onde o calendário será renderizado
var calendarEl = document.getElementById('calendar');

// Inicializa o calendário usando a biblioteca FullCalendar
var calendar = new FullCalendar.Calendar(calendarEl, {
    // Configura a visualização inicial para o mês na grade de dias
    initialView: 'dayGridMonth',

    // Função para recuperar os eventos do arquivo JSON
    events: function (info, successCallback, failureCallback) {
        fetch(request_calendar)
            .then(function (response) {
                return response.json()
            })
            .then(function (data) {
                // Mapeia os dados dos eventos para o formato esperado pelo FullCalendar
                let events = data.events.map(function (event) {
                    return {
                        title: event.eventTitle,
                        start: new Date(event.eventStartDate),
                        end: new Date(event.eventEndDate),
                        url: event.eventUrl,
                        location: event.eventLocation,
                        timeStart: event.eventStartTime,
                        timeEnd: event.eventEndTime,
                    }
                })
                // Chama a função de retorno de sucesso com os eventos recuperados
                successCallback(events)
            })
            .catch(function (error) {
                // Chama a função de retorno de falha em caso de erro na solicitação
                failureCallback(error)
            })
    },

    // Define o conteúdo personalizado para cada evento no calendário
    eventContent: function (info) {
        // Retorna o HTML personalizado para exibir informações do evento
        return {
            html: `
                <div style="overflow: hidden; font-size: 12px; positon: relative;  cursor: pointer; font-family: 'Inter', sans-serif;">
                    <div><strong>${info.event.title}</strong></div>
                    <div>Location: ${info.event.extendedProps.location}</div>
                    <div>Date: ${info.event.start.toLocaleDateString(
                "es-US",
                {
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                }
            )}</div>
                    <div>Time: ${info.event.extendedProps.timeStart} - ${info.event.extendedProps.timeEnd}</div>
                </div>
                `
        }
    },

    // Evento acionado quando o mouse entra em um evento do calendário
    eventMouseEnter: function (mouseEnterInfo) {
        // Adiciona uma classe CSS e cria um elemento HTML para exibir informações adicionais do evento
        let el = mouseEnterInfo.el
        el.classList.add("relative")

        let newEl = document.createElement("div")
        let newElTitle = mouseEnterInfo.event.title
        let newElLocation = mouseEnterInfo.event.extendedProps.location
        newEl.innerHTML = `
                <div
                    class="fc-hoverable-event"
                    style="position: absolute; bottom: 100%; left: 0; width: 300px; height: auto; background-color: white; z-index: 50; border: 1px solid #e2e8f0; border-radius: 0.375rem; padding: 0.75rem; font-size: 14px; font-family: 'Inter', sans-serif; cursor: pointer;"
                >
                    <strong>${newElTitle}</strong>
                    <div>Location: ${newElLocation}</div>

                </div>
            `
        el.after(newEl)
    },

    // Evento acionado quando o mouse sai de um evento do calendário
    eventMouseLeave: function () {
        // Remove o elemento HTML que exibe informações adicionais do evento
        document.querySelector(".fc-hoverable-event").remove()
    }
});

// Renderiza o calendário na página
calendar.render();
