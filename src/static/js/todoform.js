 // add an event listener to the form that will be called when the form is submitted
 document.getElementById('todo-form').addEventListener('submit', function(event) {
    // prevent the form from being submitted and refreshing the page
    event.preventDefault();

    // get the value of the input field
    const newItem = document.getElementById('todo-input').value;

    // add the new item to the list
    addItemToList(newItem);
  });

// create a new Set to store the list items
const itemSet = new Set();

function addItemToList(itemText) {
  {
    itemSet.add(itemText);

    const list = document.getElementById('todo-list');

    // create a new li element
    const newItem = document.createElement('li');
    newItem.classList.add('flex', 'items-center', 'mb-4');
    newItem.innerHTML = `
      <input type="checkbox" class="form-checkbox h-4 w-4 text-indigo-600 transition duration-150 ease-in-out" />
      <label class="ml-2 block text-gray-700 font-medium">${itemText}</label>
    `;

    // add the new li element to the end of the list
    list.appendChild(newItem);
    // send an HTTP request to a Python script with the added item text
    fetch('/', {
      method: 'POST',
      body: JSON.stringify({ item: itemText }),
      headers: { 'Content-Type': 'application/json' }
    });

    // clear the input field
    document.getElementById('todo-input').value = '';
  }
}

// add an event listener to the "Clear Completed" button
document.querySelector('.btn-secondary').addEventListener('click', function() {
  // get all of the checked checkboxes in the list
  const checkedBoxes = document.querySelectorAll('#todo-list input:checked');

  // remove the parent li element for each checked checkbox
  // and add the removed item to the removedList
  Array.from(checkedBoxes).forEach(box => {
    const itemText = box.nextSibling.textContent;
    console.log(itemText);
    itemSet.delete(itemText);
    box.parentElement.remove();
    
  });
});