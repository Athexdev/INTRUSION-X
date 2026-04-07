document.addEventListener('DOMContentLoaded', () => {
    // --------------------------------------------------------
    // STATE MANAGEMENT
    // --------------------------------------------------------
    let isAttackMode = false;
    let packetCount = 842000;
    let threatsDetected = 0;
    
    // --------------------------------------------------------
    // THREE.JS SETUP (RETAINED ORIGINAL GLOBE)
    // --------------------------------------------------------
    const container = document.getElementById('canvas-container');
    if (!container) return;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x020617, 0.02);

    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 0, 15);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const universeGroup = new THREE.Group();
    const globeGroup = new THREE.Group();
    universeGroup.add(globeGroup);
    scene.add(universeGroup);

    // --- 1. STARS BACKGROUND ---
    const starsGeometry = new THREE.BufferGeometry();
    const starsCount = 1500;
    const posArray = new Float32Array(starsCount * 3);
    for(let i = 0; i < starsCount * 3; i++) posArray[i] = (Math.random() - 0.5) * 80;
    starsGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    
    const starsMaterial = new THREE.PointsMaterial({
        size: 0.05,
        color: 0xffffff,
        transparent: true,
        opacity: 0.8
    });
    const starMesh = new THREE.Points(starsGeometry, starsMaterial);
    universeGroup.add(starMesh);

    // --- 2. ORIGINAL EARTH ---
    const geometry = new THREE.SphereGeometry(5, 64, 64);
    const textureLoader = new THREE.TextureLoader();
    
    const earthTexture = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg');
    const specTexture = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_specular_2048.jpg');
    const normalTexture = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_normal_2048.jpg');
    const lightsTexture = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_lights_2048.png');
    const cloudsTexture = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_clouds_1024.png');

    const material = new THREE.MeshPhongMaterial({
        map: earthTexture,
        specularMap: specTexture,
        normalMap: normalTexture,
        emissiveMap: lightsTexture,
        emissive: 0xffcc33,
        emissiveIntensity: 0.6,
        color: 0x152030,
        specular: 0x555555,
        shininess: 10
    });
    const globe = new THREE.Mesh(geometry, material);
    globeGroup.add(globe);

    // --- 3. CLOUDS ---
    const cloudGeo = new THREE.SphereGeometry(5.08, 64, 64);
    const cloudMat = new THREE.MeshLambertMaterial({
        map: cloudsTexture,
        transparent: true,
        opacity: 0.4,
        blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide
    });
    const cloudMesh = new THREE.Mesh(cloudGeo, cloudMat);
    globeGroup.add(cloudMesh);

    // --- 4. ATMOSPHERE GLOW ---
    const atmosphereGeo = new THREE.SphereGeometry(5.2, 64, 64);
    const atmosphereMat = new THREE.ShaderMaterial({
        vertexShader: `
            varying vec3 vNormal;
            void main() {
                vNormal = normalize(normalMatrix * normal);
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            varying vec3 vNormal;
            void main() {
                float intensity = pow(0.6 - dot(vNormal, vec3(0, 0, 1.0)), 3.0);
                gl_FragColor = vec4(0.96, 0.62, 0.04, 1.0) * intensity * 1.5;
            }
        `,
        blending: THREE.AdditiveBlending,
        side: THREE.BackSide,
        transparent: true
    });
    const atmosphere = new THREE.Mesh(atmosphereGeo, atmosphereMat);
    globeGroup.add(atmosphere);

    // --- 5. CONNECTIONS ---
    const connectionsGroup = new THREE.Group();
    globeGroup.add(connectionsGroup);
    const trafficParticles = [];

    function latLonToVector3(lat, lon, radius) {
        const phi = (90 - lat) * (Math.PI / 180);
        const theta = (lon + 180) * (Math.PI / 180);
        return new THREE.Vector3(
            -(radius * Math.sin(phi) * Math.cos(theta)),
            (radius * Math.cos(phi)),
            (radius * Math.sin(phi) * Math.sin(theta))
        );
    }

    function createArc(startLat, startLon, endLat, endLon) {
        const start = latLonToVector3(startLat, startLon, 5);
        const end = latLonToVector3(endLat, endLon, 5);
        const dist = start.distanceTo(end);
        const mid = start.clone().add(end).multiplyScalar(0.5).normalize().multiplyScalar(5 + (dist * 0.2));
        const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
        const points = curve.getPoints(50);
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        
        const material = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.1 });
        const line = new THREE.Line(geometry, material);
        connectionsGroup.add(line);

        const particleGeo = new THREE.SphereGeometry(0.06, 8, 8);
        const particleMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b });
        const particle = new THREE.Mesh(particleGeo, particleMat);
        connectionsGroup.add(particle);
        
        trafficParticles.push({ mesh: particle, curve: curve, progress: Math.random() });
    }

    const cities = [
        {lat: 40.71, lon: -74.00}, {lat: 51.50, lon: -0.12},
        {lat: 35.68, lon: 139.69}, {lat: -33.86, lon: 151.20},
        {lat: -22.90, lon: -43.17}, {lat: 25.20, lon: 55.27},
        {lat: 1.35, lon: 103.81}, {lat: 48.85, lon: 2.35},
        {lat: 37.77, lon: -122.41}, {lat: 19.07, lon: 72.87}
    ];

    function initGlobeElements() {
        connectionsGroup.clear();
        trafficParticles.length = 0;
        cities.forEach(city => {
            const pos = latLonToVector3(city.lat, city.lon, 5.01);
            const markerGeo = new THREE.RingGeometry(0.06, 0.08, 32);
            const markerMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b, side: THREE.DoubleSide });
            const marker = new THREE.Mesh(markerGeo, markerMat);
            marker.position.copy(pos);
            marker.lookAt(0,0,0);
            globeGroup.add(marker);

            // Arcs
            for(let k=0; k<1; k++) {
                const target = cities[Math.floor(Math.random() * cities.length)];
                createArc(city.lat, city.lon, target.lat, target.lon);
            }
        });
    }
    initGlobeElements();

    // --- LIGHTING ---
    scene.add(new THREE.AmbientLight(0x050505));
    const sunLight = new THREE.DirectionalLight(0xffffff, 1.2);
    sunLight.position.set(10, 5, 10);
    scene.add(sunLight);
    const rimLight = new THREE.SpotLight(0xf59e0b, 8);
    rimLight.position.set(-10, 10, -5);
    rimLight.lookAt(0,0,0);
    scene.add(rimLight);

    // --- ANIMATION ---
    let mouseX = 0, mouseY = 0;
    window.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
    });

    function animate() {
        requestAnimationFrame(animate);
        globe.rotation.y += 0.0005;
        cloudMesh.rotation.y += 0.0007;
        atmosphere.rotation.y += 0.0005;

        trafficParticles.forEach(p => {
            p.progress += 0.004;
            if(p.progress > 1) p.progress = 0;
            p.mesh.position.copy(p.curve.getPoint(p.progress));
        });

        starMesh.rotation.y -= 0.0002;
        gsap.to(universeGroup.rotation, {
            x: mouseY * 0.1,
            y: mouseX * 0.1,
            duration: 1,
            ease: "power2.out"
        });

        renderer.render(scene, camera);
    }
    animate();

    // --------------------------------------------------------
    // NIDS SIMULATION LOGIC
    // --------------------------------------------------------
    const terminal = document.getElementById('terminal-output');
    const trafficStream = document.getElementById('traffic-stream');
    const logs = [
        "Inbound connection from 185.220.101.42 (Tor Exit Node)",
        "Packet filtered: SYN flood detected from segment 10.4.0.0/24",
        "Heuristic analysis complete: 0 anomalies found",
        "Deep packet inspection active on Port 443",
        "Auth failure: root access attempted from unknown IP",
        "Database sync complete with Global Threat Intel"
    ];
    const threatLogs = [
        "CRITICAL: SQL Injection attempt detected",
        "WARNING: Unexpected spike in UDP traffic",
        "ALERT: Unauthorized administrative login",
        "MALWARE: Signature match for Trojan.Generic",
        "DDoS ATTACK: Protocol violation detected"
    ];

    function addLog(text, type = 'normal') {
        const div = document.createElement('div');
        div.className = type === 'threat' ? 'text-red-500 font-bold' : 'text-emerald-500/80';
        div.innerHTML = `<span class="text-zinc-600">[${new Date().toLocaleTimeString()}]</span> ${text}`;
        terminal.appendChild(div);
        terminal.scrollTop = terminal.scrollHeight;
        if (terminal.childNodes.length > 50) terminal.removeChild(terminal.firstChild);
    }

    function addPacket() {
        const ips = ["10.0.0.1", "192.168.1.45", "172.16.0.12", "8.8.8.8", "142.250.1.1"];
        const proto = ["TCP", "UDP", "ICMP", "HTTPS", "SSH"];
        const src = ips[Math.floor(Math.random() * ips.length)];
        const dest = ips[Math.floor(Math.random() * ips.length)];
        const pr = proto[Math.floor(Math.random() * proto.length)];
        
        const div = document.createElement('div');
        const isThreat = isAttackMode && Math.random() > 0.7;
        div.className = `glass-card p-3 rounded flex justify-between items-center text-[10px] border-l-2 ${isThreat ? 'border-red-500 bg-red-500/5' : 'border-emerald-500/30'}`;
        div.innerHTML = `
            <span class="${isThreat ? 'text-red-400' : 'text-emerald-400'}">[${src}] -> [${dest}]</span>
            <span class="text-zinc-500 uppercase">${pr}</span>
            <span class="${isThreat ? 'text-red-500 font-bold' : 'text-emerald-500/50'}">${isThreat ? 'MALICIOUS' : 'SECURE'}</span>
        `;
        trafficStream.prepend(div);
        if (trafficStream.childNodes.length > 8) trafficStream.removeChild(trafficStream.lastChild);

        if (isThreat) {
            threatsDetected++;
            document.getElementById('stat-alerts').innerText = threatsDetected;
            addLog(threatLogs[Math.floor(Math.random() * threatLogs.length)], 'threat');
        }
    }

    setInterval(() => addLog(logs[Math.floor(Math.random() * logs.length)]), 3000);
    setInterval(() => {
        addPacket();
        packetCount += Math.floor(Math.random() * 10);
        document.getElementById('stat-packets').innerText = (packetCount / 1000).toFixed(1) + "K";
        document.getElementById('nav-packet-count').innerText = Math.floor(500 + Math.random() * 2000);
    }, 800);

    // --------------------------------------------------------
    // UI INTERACTION
    // --------------------------------------------------------
    const modeToggle = document.getElementById('mode-toggle');
    modeToggle.addEventListener('click', () => {
        isAttackMode = !isAttackMode;
        modeToggle.classList.toggle('active');
        
        const heroTitle = document.getElementById('hero-title');
        const scanningText = document.getElementById('scanning-text');
        
        if (isAttackMode) {
            heroTitle.className = 'alert-text-gradient';
            scanningText.innerText = "ATTACK SIMULATION ACTIVE";
            scanningText.classList.add('text-red-500');
            addLog("SYSTEM ALERT: Simulation mode engaged.", "threat");
        } else {
            heroTitle.className = 'cyber-text-gradient';
            scanningText.innerText = "Scanning Network Nodes...";
            scanningText.classList.remove('text-red-500');
            addLog("SYSTEM INFO: Simulation mode disengaged.");
        }
    });

    // GSAP SCROLL TRIGGERS
    gsap.registerPlugin(ScrollTrigger);
    globeGroup.rotation.x = 0.2;
    globeGroup.rotation.y = 4.5;
    
    const tl = gsap.timeline({
        scrollTrigger: {
            trigger: "body",
            start: "top top",
            end: "bottom bottom",
            scrub: 1
        }
    });

    tl.to(globeGroup.position, { x: -3.5, z: -2, duration: 5 })
      .to(globeGroup.rotation, { y: "+=1.5", x: 0.4, duration: 5 })
      .to(globeGroup.position, { x: -4, y: 1, z: -3, duration: 5 })
      .to(globeGroup.rotation, { y: "+=1.2", x: -0.2, duration: 5 })
      .to(globeGroup.position, { x: 0, y: -6, z: 2, duration: 5 })
      .to(globeGroup.rotation, { y: "+=1.0", x: 0.5, duration: 5 });

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
});
