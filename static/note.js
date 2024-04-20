/* All the elements that the script will deal with*/
const delete_button = document.getElementById('delete-button');
const markdown_box = document.getElementById('markdown');
const render_window = document.getElementById('content-frame').contentWindow.document;
const save_button = document.getElementById('save-button');
const title_input = document.getElementById('title-in');
const the_title = document.getElementById('the-title');

/* Function to delete the note by title */
function delete_it() {
    /* Guard against accidental deletion by just checking if the button is not in its default state */
    if (delete_button.textContent != "Delete") {
        /* Set up the request to delete */
        const base = window.location.origin;
        const data = {'Title': title_input.value};

        /* Tell the server to delete it */
        fetch(`${base}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                },
            body: JSON.stringify(data),
            }).then(response => {
                /* If the response is not OK, throw an error */
                if (!response.ok) {
                    delete_button.textContent = 'Error';
                    throw new Error('Server could not delete.');
                }
                /* Otherwise, redirect to the home page */
                else {
                    window.location.href = base;
                }
            /* Catch errors that may arise */
            }).catch(error => {
                console.error('There was a problem with the fetch operation:', error);
        });
    /* Clause to guard the user from deleting accidentally */
    } else {
        delete_button.textContent = "Sure?";
    }
};

/* Calls the markdown renderer */
function render() {
    /* Open and replace the iframe with the newly rendered markdown */
    render_window.open();
    render_window.write(`<html><head><link rel="stylesheet" type="text/css" href="/static/styles.css"></head><body>${marked.parse(markdown_box.value)}</body></html>`);
    render_window.close();
    /* Make the iframe follow the page's current theme */
    render_window.querySelector("html").setAttribute("data-theme", currentThemeSetting);
};

/* Saves a note based on its title */
function save() {
    /* Guard clause to prevent re-saving */
    if (save_button.textContent == 'Saved') { return; }
    /* Set up the request to save */
    const base = window.location.origin;
    const data = {'Title': title_input.value, 'Content': markdown_box.value};

    /* Tell the server to save it */
    fetch(`${base}/save`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            },
        body: JSON.stringify(data),
        }).then(response => {
            /* Make sure we saved it according to the server */
            if (!response.ok) {
                save_button.textContent = 'Error';
                throw new Error('Server could not save.');
            }
            /* If it was saved, make the button indicate so*/
            else {
                save_button.textContent = 'Saved';
            }
        }).catch(error => {
            console.error('There was a problem with the fetch operation:', error);
    });
};

/* The event listeners for various function callbacks */
markdown_box.addEventListener('input', () => {render(); save_button.textContent = 'Save';});
save_button.addEventListener('click', () => {save();});
delete_button.addEventListener('click', () => {delete_it();});
title_input.addEventListener('input', () => {the_title.innerHTML = title_input.value;  save_button.textContent = 'Save';});

/* First render call to actually render the markdown content from the server (if any) */
render();

/* Call the save function every 30 seconds (autosave) */
setInterval(save, 30000);