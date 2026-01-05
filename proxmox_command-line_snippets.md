---
title: "Proxmox Command-Line Snippets"
---

# Proxmox Command-Line Snippets

The following table provides a handy list of Proxmox commands.

<table>
  <tr>
    <th>Description</th>
    <th>Command</th>
  </tr>

  <!-- List VMs -->
  <tr>
    <td>
        List all virtual machines hosted in a Proxmox node.
    </td>
    <td>
      <pre><code class="language-bash">
for vm in $(sudo qm list | awk 'NR>1 {print $1}'); do echo "$vm"; done
      </code></pre>
    </td>
  </tr>

  <!-- VM Status -->
  <tr>
    <td>
        Show detailed status for a specific VM.
    </td>
    <td>
      <pre><code class="language-bash">
qm status &lt;VMID&gt;
      </code></pre>
    </td>
  </tr>

  <!-- VM Config -->
  <tr>
    <td>
        Display the full configuration of a VM.
    </td>
    <td>
      <pre><code class="language-bash">
qm config &lt;VMID&gt;
      </code></pre>
    </td>
  </tr>

  <!-- Start VM -->
  <tr>
    <td>
        Start a virtual machine.
    </td>
    <td>
      <pre><code class="language-bash">
qm start &lt;VMID&gt;
      </code></pre>
    </td>
  </tr>

  <!-- Stop VM -->
  <tr>
    <td>
        Stop a virtual machine (graceful shutdown).
    </td>
    <td>
      <pre><code class="language-bash">
qm shutdown &lt;VMID&gt;
      </code></pre>
    </td>
  </tr>

  <!-- Force Stop VM -->
  <tr>
    <td>
        Force-stop a VM (equivalent to pulling the power).
    </td>
    <td>
      <pre><code class="language-bash">
qm stop &lt;VMID&gt;
      </code></pre>
    </td>
  </tr>

  <!-- Migrate VM -->
  <tr>
    <td>
        Migrate a VM to another node (online/live migration).
    </td>
    <td>
      <pre><code class="language-bash">
qm migrate &lt;VMID&gt; &lt;target-node&gt; --online
      </code></pre>
    </td>
  </tr>

  <!-- Node Health -->
  <tr>
    <td>
        Show node resource usage (CPU, RAM, storage).
    </td>
    <td>
      <pre><code class="language-bash">
pvesh get /nodes/$(hostname)/status
      </code></pre>
    </td>
  </tr>

  <!-- Storage List -->
  <tr>
    <td>
        List all storage backends available on the node.
    </td>
    <td>
      <pre><code class="language-bash">
pvesm status
      </code></pre>
    </td>
  </tr>

  <!-- Cluster Nodes -->
  <tr>
    <td>
        List all nodes in the Proxmox cluster.
    </td>
    <td>
      <pre><code class="language-bash">
pvecm nodes
      </code></pre>
    </td>
  </tr>

  <!-- Cluster Status -->
  <tr>
    <td>
        Display cluster quorum and corosync status.
    </td>
    <td>
      <pre><code class="language-bash">
pvecm status
      </code></pre>
    </td>
  </tr>

</table>

