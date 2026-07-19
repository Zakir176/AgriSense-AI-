export const externalTooltipHandler = (context) => {
  // Tooltip Element
  const { chart, tooltip } = context;
  let tooltipEl = chart.canvas.parentNode.querySelector('div.chartjs-tooltip');

  if (!tooltipEl) {
    tooltipEl = document.createElement('div');
    tooltipEl.classList.add('chartjs-tooltip');
    tooltipEl.style.background = 'rgba(255, 255, 255, 0.7)';
    tooltipEl.style.backdropFilter = 'blur(12px)';
    tooltipEl.style.webkitBackdropFilter = 'blur(12px)';
    tooltipEl.style.borderRadius = '12px';
    tooltipEl.style.color = '#1f2937'; // gray-800
    tooltipEl.style.opacity = 1;
    tooltipEl.style.pointerEvents = 'none';
    tooltipEl.style.position = 'absolute';
    tooltipEl.style.transform = 'translate(-50%, -100%)';
    tooltipEl.style.marginTop = '-10px';
    tooltipEl.style.transition = 'all .2s ease';
    tooltipEl.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)';
    tooltipEl.style.border = '1px solid rgba(0, 0, 0, 0.05)';
    tooltipEl.style.padding = '12px';
    tooltipEl.style.zIndex = 100;
    
    // Dark mode check
    if (document.documentElement.classList.contains('dark')) {
      tooltipEl.style.background = 'rgba(27, 27, 30, 0.7)';
      tooltipEl.style.color = '#f9fafb'; // gray-50
      tooltipEl.style.border = '1px solid rgba(255, 255, 255, 0.1)';
    }

    chart.canvas.parentNode.appendChild(tooltipEl);
  }

  // Hide if no tooltip
  if (tooltip.opacity === 0) {
    tooltipEl.style.opacity = 0;
    return;
  }

  // Set Text
  if (tooltip.body) {
    const titleLines = tooltip.title || [];
    const bodyLines = tooltip.body.map(b => b.lines);

    let innerHtml = '<div style="font-family: \'Plus Jakarta Sans\', sans-serif;">';

    titleLines.forEach(title => {
      innerHtml += `<div style="font-weight: 800; font-size: 13px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; color: ${document.documentElement.classList.contains('dark') ? '#9ca3af' : '#6b7280'};">${title}</div>`;
    });

    bodyLines.forEach((body, i) => {
      const colors = tooltip.labelColors[i];
      const style = `
        background: ${colors.backgroundColor};
        border-color: ${colors.borderColor || 'transparent'};
        border-width: 2px;
        width: 12px;
        height: 12px;
        display: inline-block;
        border-radius: 4px;
        margin-right: 8px;
        vertical-align: middle;
      `;
      innerHtml += `<div style="display: flex; align-items: center; font-size: 14px; font-weight: 600; margin-bottom: 4px;"><span style="${style}"></span>${body}</div>`;
    });
    
    innerHtml += `<div style="margin-top: 8px; font-size: 10px; color: ${document.documentElement.classList.contains('dark') ? '#6b7280' : '#9ca3af'}; font-weight: 600;">Click point for details</div>`;
    innerHtml += '</div>';

    tooltipEl.innerHTML = innerHtml;
  }

  const position = context.chart.canvas.getBoundingClientRect();

  // Display, position, and set styles for font
  tooltipEl.style.opacity = 1;
  tooltipEl.style.left = tooltip.caretX + 'px';
  tooltipEl.style.top = tooltip.caretY + 'px';
};
