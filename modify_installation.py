import re

file_path = '/www/wwwroot/rarayvision.dfs.co.id/frontend/src/views/InstallationView.vue'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Update <script setup>
script_setup_old = """<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  window.scrollTo(0, 0)
})
</script>"""

script_setup_new = """<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  window.scrollTo(0, 0)
})

const copyCode = (event) => {
  const container = event.currentTarget.parentElement;
  const preEl = container.querySelector('pre');
  if (preEl) {
    navigator.clipboard.writeText(preEl.innerText).then(() => {
      const iconSpan = event.currentTarget.querySelector('.icon');
      if (iconSpan) {
        const originalHTML = iconSpan.innerHTML;
        iconSpan.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#4ade80" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`;
        setTimeout(() => {
          iconSpan.innerHTML = originalHTML;
        }, 2000);
      }
    });
  }
}
</script>"""

content = content.replace(script_setup_old, script_setup_new)

# 2. Add button to .code-block elements
btn_html = '''
  <button class="copy-btn" @click="copyCode($event)" title="Copy code">
    <span class="icon">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
    </span>
  </button>'''

def replacer(match):
    indent = match.group(1)
    tag = match.group(2)
    btn = btn_html.replace('\n', '\n' + indent)
    return f"{indent}{tag}{btn}"

content = re.sub(r'^([ \t]*)(<div class="code-block"[^>]*>)', replacer, content, flags=re.MULTILINE)

# 3. Update CSS
css_old = """/* Code blocks */
.code-block {
  background: #0f172a;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  overflow-x: auto;
}"""

css_new = """/* Code blocks */
.code-block {
  background: #0f172a;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  overflow-x: auto;
  position: relative;
}
.copy-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.copy-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}"""

content = content.replace(css_old, css_new)

with open(file_path, 'w') as f:
    f.write(content)

print("InstallationView.vue updated successfully.")
