document.getElementById('birthForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;
    const zipcode = document.getElementById('zipcode').value;

    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.loader');
    const errorContainer = document.getElementById('errorContainer');
    const resultsContainer = document.getElementById('resultsContainer');

    // UI Loading state
    btnText.classList.add('hidden');
    loader.classList.remove('hidden');
    submitBtn.disabled = true;
    errorContainer.classList.add('hidden');
    resultsContainer.classList.add('hidden');

    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ date, time, zip_code: zipcode })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed to calculate chart');
        }

        const data = await response.json();
        
        // Render data
        renderChart(data);
        
        // Show results
        resultsContainer.classList.remove('hidden');
        
        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (error) {
        errorContainer.textContent = error.message;
        errorContainer.classList.remove('hidden');
    } finally {
        // Reset UI
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
        submitBtn.disabled = false;
    }
});

function renderChart(data) {
    // Basic Info
    document.getElementById('typeProfile').textContent = `${data.profile} ${data.type}`;
    
    // Cross
    if (data.cross) {
        document.getElementById('crossDetails').textContent = `${data.cross.name} (${data.cross.geometry})`;
    } else {
        document.getElementById('crossDetails').textContent = '';
    }

    // Attributes
    document.getElementById('authVal').textContent = data.authority;
    document.getElementById('stratVal').textContent = data.strategy;
    document.getElementById('sigVal').textContent = data.signature;
    document.getElementById('notSelfVal').textContent = data.not_self_theme;
    document.getElementById('defVal').textContent = data.definitions;

    // Centers
    const centersList = document.getElementById('centersList');
    centersList.innerHTML = '';
    if (data.centers && data.centers.length > 0) {
        data.centers.forEach(center => {
            const pill = document.createElement('div');
            pill.className = 'pill';
            pill.textContent = center;
            centersList.appendChild(pill);
        });
    } else {
        centersList.innerHTML = '<span class="text-muted">No defined centers</span>';
    }

    // Channels
    const channelsEl = document.getElementById('channelsList');
    channelsEl.innerHTML = '';
    if (data.channels && data.channels.length > 0) {
        data.channels.forEach(ch => {
            const li = document.createElement('li');
            li.textContent = `${ch.gates[0]}-${ch.gates[1]}: ${ch.name}`;
            channelsEl.appendChild(li);
        });
    } else {
        channelsEl.innerHTML = '<li>No defined channels</li>';
    }

    // Variables
    const variablesEl = document.getElementById('variablesList');
    variablesEl.innerHTML = '';
    if (data.variables) {
        const v = data.variables;
        const vars = [
            `Determination: ${v.determination}`,
            `Cognition: ${v.cognition}`,
            `Environment: ${v.environment}`,
            `Perspective: ${v.perspective}`,
            `Motivation: ${v.motivation}`,
            `Sense: ${v.sense}`
        ];
        vars.forEach(vStr => {
            const li = document.createElement('li');
            li.textContent = vStr;
            variablesEl.appendChild(li);
        });
    } else {
        variablesEl.innerHTML = '<li>No variable data available</li>';
    }
}
