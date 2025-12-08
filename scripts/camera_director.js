import { world, system, Vector } from "@minecraft/server";

// Settings
const CAMERA_TAG = "cameraman";
const SWITCH_INTERVAL = 200; // 10 seconds (20 ticks * 10)
const CAMERA_DISTANCE = 10;
const CAMERA_HEIGHT = 5;

let currentTarget = null;
let switchTimer = 0;

system.runInterval(() => {
    // 1. Find CameraMan
    const cameramen = world.getPlayers({ tags: [CAMERA_TAG] });
    if (cameramen.length === 0) return;

    // We assume single camera man for now
    const cam = cameramen[0];

    // 2. Select Target (Round Robin or Random)
    switchTimer++;
    if (switchTimer >= SWITCH_INTERVAL || !currentTarget || !isValidTarget(currentTarget)) {
        switchTimer = 0;
        pickNewTarget(cam);
    }

    if (currentTarget && isValidTarget(currentTarget)) {
        updateCameraPosition(cam, currentTarget);
    } else {
        // Fallback: Reset camera if no target
        cam.camera.clear();
    }
});

function isValidTarget(target) {
    try {
        if (!target.isValid()) return false;
        // Don't film other cameramen or dead/spectators
        if (target.hasTag(CAMERA_TAG)) return false;
        // Check gamemode? (Hard to check via API directly without properties)
        return true;
    } catch { return false; }
}

function pickNewTarget(cam) {
    const players = world.getAllPlayers().filter(p => !p.hasTag(CAMERA_TAG));
    if (players.length === 0) {
        currentTarget = null;
        return;
    }

    // Random pick
    const idx = Math.floor(Math.random() * players.length);
    currentTarget = players[idx];

    // Notification (Optional)
    // cam.onScreenDisplay.setActionBar(`🎥 Now filming: ${currentTarget.name}`);
}

function updateCameraPosition(cam, target) {
    const tLoc = target.location;
    const tRot = target.getRotation(); // {x, y}

    // Calculate generic "behind and up" position
    // We want to be behind the player.
    // Yaw (y) in MC: 0=South(+Z), 90=West(-X), 180=North(-Z), 270=East(+X)
    // We need to convert to radians.

    const radY = (tRot.y + 90) * (Math.PI / 180);
    // Wait, MC standard rotation math is tricky. 
    // Simply: Direction vector from rotation.
    // But let's just make it a "Drone" that hovers at fixed offset relative to view?
    // "10 blocks away" -> -Direction * 10

    const viewDir = getViewDirection(tRot.y, tRot.x);

    // Camera Pos = TargetPos - (ViewDir * Dist) + (Up * Height)
    const cX = tLoc.x - (viewDir.x * CAMERA_DISTANCE);
    const cY = tLoc.y + CAMERA_HEIGHT;
    const cZ = tLoc.z - (viewDir.z * CAMERA_DISTANCE);

    // Apply Camera
    // 'minecraft:free' camera allows custom placement
    // easeOptions can make it smooth
    cam.camera.setCamera("minecraft:free", {
        location: { x: cX, y: cY, z: cZ },
        facing: target, // Look AT the target entity
        easeOptions: {
            easeTime: 0.5, // Smooth update every tick? Might incur lag if too frequent.
            easeType: "Linear"
        }
    });
}

function getViewDirection(yRot, xRot) {
    const checkY = yRot + 90; // Adjust for math
    const radY = checkY * (Math.PI / 180);
    const radX = -xRot * (Math.PI / 180); // Pitch is inverted often

    const cosX = Math.cos(radX);

    return {
        x: Math.cos(radY) * cosX,
        y: Math.sin(radX),
        z: Math.sin(radY) * cosX
    };
}
