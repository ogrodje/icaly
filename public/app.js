'use strict';

window.addEventListener('DOMContentLoaded', () => {
  const origin = window.location.origin;
  const icsUrl = origin + '/calendar.ics';
  const googleLink =
    'https://calendar.google.com/calendar/u/0/r?cid=' + encodeURIComponent(icsUrl);

  const calendarLink = document.getElementById('google-calendar');
  const downloadLink = document.getElementById('ics-download');
  const eventsListElement = document.getElementById('events-list');

  if (calendarLink) {
    calendarLink.href = googleLink;
  }

  if (downloadLink) {
    downloadLink.href = icsUrl;
  }

  if (!eventsListElement) {
    return;
  }

  fetch('/api/events', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then((response) => {
      if (!response.ok) {
        throw new Error('Failed to load events');
      }
      return response.json();
    })
    .then((events) => {
      if (!Array.isArray(events) || events.length === 0) {
        eventsListElement.innerHTML = '<p>No upcoming events found.</p>';
        return;
      }

      eventsListElement.innerHTML = '';
      for (const event of events) {
        const wrapper = document.createElement('article');
        wrapper.className = 'event';

        const title = document.createElement('h3');
        title.textContent = (event.source ? '[' + event.source + '] ' : '') + event.title;
        wrapper.appendChild(title);

        const time = document.createElement('time');
        time.dateTime = event.startDateTime;
        const end = event.endDateTime ? new Date(event.endDateTime) : null;
        const formatter = new Intl.DateTimeFormat(undefined, {
          dateStyle: 'medium',
          timeStyle: event.hasStartTime ? 'short' : undefined,
        });

        const startLabel = event.startDateTime
          ? formatter.format(new Date(event.startDateTime))
          : 'Unknown start';
        const endLabel =
          end && !Number.isNaN(end.valueOf())
            ? formatter.format(end)
            : event.hasEndTime
            ? 'Unknown end'
            : null;

        time.textContent = endLabel ? `${startLabel} → ${endLabel}` : startLabel;
        wrapper.appendChild(time);

        if (event.locationName) {
          const location = document.createElement('p');
          location.textContent = event.locationAddress
            ? `${event.locationName} – ${event.locationAddress}`
            : event.locationName;
          wrapper.appendChild(location);
        }

        if (event.eventURL) {
          const link = document.createElement('a');
          link.href = event.eventURL;
          link.textContent = 'Event website';
          link.target = '_blank';
          link.rel = 'noopener';
          wrapper.appendChild(link);
        }

        eventsListElement.appendChild(wrapper);
      }
    })
    .catch((error) => {
      console.error(error);
      eventsListElement.innerHTML =
        '<p>There was a problem loading the event feed. The calendar link will still work.</p>';
    });
});
