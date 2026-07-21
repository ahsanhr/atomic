import NavBar from "../components/Navbar";
import Hub from "./Hub.jsx"
import LevelUpModal from "../components/LevelUpModal";
import { getRoom, getQuests, completeQuest } from "../api";
import "../room.css";
import { 
  Canvas, 
  useFrame, 
  useThree 
} from "@react-three/fiber";
import { 
  useRef,
  useState,
  useEffect
 } from "react";
import {
  OrbitControls,
  GizmoHelper,
  GizmoViewcube,
  GizmoViewport,
  useHelper,
  useGLTF,
  useAnimations
} from "@react-three/drei";
import { useControls } from "leva";
import { 
  SpotLightHelper, 
  DirectionalLightHelper, 
  CameraHelper
} from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import * as THREE from 'three';
import { 
  EffectComposer, 
  Outline, 
  Selection, 
  Select 
} from '@react-three/postprocessing';
import { createPortal } from 'react-dom';
function Light() {
  const light = useRef();
  const shadow = useRef();

  // const {position, rotation, intensity } = useControls({
  //   position: [17, 15, 7],
  //   rotation: 0.6,
  //   intensity: 2000
  // });

  const {position, rotation, intensity } = ({
    position: [17, 15, 7],
    rotation: 0.6,
    intensity: 2000
  });

  
  return (
    <spotLight
    ref={light}
    angle={rotation}
    position={position}
    intensity={intensity}
    castShadow
    >
      <orthographicCamera attach='shadow-camera' ref={shadow} top={8} right={8} />
    </spotLight> 
  );
}
// use for example:
function AnimatedBox() {
  const boxRef = useRef();

  const { color, speed } = useControls({
    color: "#00bfff",
    speed: {
      value: 0.005,
      min: 0,
      max: 0.2,
      step: 0.001,
    },
  });

  useFrame(() => {
    boxRef.current.rotation.x += speed;
    boxRef.current.rotation.y += speed;
    boxRef.current.rotation.z += speed;
  });

  return (
    <mesh ref={boxRef} position={[5, 3, 0]} castShadow>
      <boxGeometry args={[2, 2, 2]} />
      <axesHelper args={[10]} />
      <meshStandardMaterial color={color} />
    </mesh>
  );
}
// actual objects
function AirMattress(){
  const result = useGLTF("/airmattress.glb");
  return <primitive object={result.scene} position={[0,0,0]} />;
}
function Book({ onBookClick }){
  const result = useGLTF("/book.glb");
  const [hovered, setHovered] = useState(false);

  return (
    <Select enabled={hovered}>
      <primitive 
        object={result.scene} 
        position={[0, 0, 0]} 
        onClick={(e) => {
          e.stopPropagation();
          onBookClick();
        }}
        onPointerEnter={(e) => {
          e.stopPropagation(); 
          setHovered(true);
        }}
        onPointerLeave={() => setHovered(false)} 
      />
    </Select>
  );
}
function Bookshelf(){
  const result = useGLTF("/bookshelf.glb");
  return <primitive object={result.scene} position={[0,0,0]} />;
}
function Chair(){
  const result = useGLTF("/chair.glb");
  return <primitive object={result.scene} position={[0,0,0]} />;
}
function Desk(){
  const result = useGLTF("/desk.glb");
  return <primitive object={result.scene} position={[0,0,0]} />;
}
function Lamp(){
  const result = useGLTF("/lamp.glb");
  return <primitive object={result.scene} position={[0,0,0]} />;
}
function Laptop({ onLaptopClick }){
  const result = useGLTF("/laptop.glb");
  const [hovered, setHovered] = useState(false);

  return (
    <Select enabled={hovered}>
      <primitive 
        object={result.scene} 
        position={[0, 0, 0]} 
        onClick={(e) => {
          e.stopPropagation();
          onLaptopClick();
        }}
        onPointerEnter={(e) => {
          e.stopPropagation(); 
          setHovered(true);
        }}
        onPointerLeave={() => setHovered(false)} 
      />
    </Select>
  );
}
function Plant(){
  const result = useGLTF("/plant.glb");
  return <primitive object={result.scene} position={[0,0,0]} />;
}
function Poster({ onPosterClick }){
  const result = useGLTF("/poster.glb");
  const [hovered, setHovered] = useState(false);

  return (
    <Select enabled={hovered}>
      <primitive 
        object={result.scene} 
        position={[0, 0, 0]}
        onClick={(e) => {
          e.stopPropagation();
          onPosterClick();
        }}
        onPointerEnter={(e) => {
          e.stopPropagation(); 
          setHovered(true);
        }}
        onPointerLeave={() => setHovered(false)} 
      />
    </Select>
  );
}
function Environment(){
  const result = useGLTF("/room.glb");
  return <primitive object={result.scene} position={[0,0,0]} />;
}
function Rug(){
  const result = useGLTF("/rug.glb");
  return <primitive object={result.scene} position={[0,0,0]} />;
}
function Window(){
  const result = useGLTF("/window.glb");
  return <primitive object={result.scene} position={[0,0,0]} />;
}
//helper function used for setting up camera position
function CameraLogger() {
  const { camera } = useThree()
  
  return (
    <OrbitControls 
      onChange={() => {
        const pos = camera.position.toArray().map(p => p.toFixed(2))
        const rot = camera.rotation.toArray().map(r => (r * 1).toFixed(2))
        
        console.log(`Position: [${pos}] | Rotation: [${rot}]`)
      }} 
    />
  )
}

function Avatar({currentAction}) {
  const group = useRef();
  const { scene, animations } = useGLTF('/avatar.glb');
  const { actions } = useAnimations(animations, group);

  // 2. Track walking direction (1 for right, -1 for left)
  const direction = useRef(1);
  const moveSpeed = 2; // How fast they walk (units per second)

  // Handle Animation Crossfading (same as before)
  useEffect(() => {
    const action = actions[currentAction];
    if (!action) return;

    action.reset().fadeIn(0.5).play();

    return () => {
      action.fadeOut(0.5);
    };
  }, [currentAction, actions]);

  // 3. Handle Physical Movement
  useFrame((state, delta) => {
    if (!group.current) return; // Make sure the model has loaded

    // Only move them if the Walk animation is active
    if (currentAction === 'Walk') {
      
      // Move the character along the X axis
      // We multiply by `delta` to ensure movement speed is consistent regardless of screen refresh rate
      group.current.position.x += direction.current * moveSpeed * delta;

      // Check boundaries to make them turn around
      if (group.current.position.x > 3) {
        // Too far right! Turn left.
        direction.current = -1;
        group.current.rotation.y = -Math.PI / 2; // Face left (Three.js uses radians)
      } 
      else if (group.current.position.x < -3) {
        // Too far left! Turn right.
        direction.current = 1;
        group.current.rotation.y = Math.PI / 2; // Face right
      }

    }
  });

  return (
    // Set a default rotation so the character starts facing right
    <group ref={group} dispose={null} >
      <primitive object={scene} position={[0,0,0]} />
    </group>
  );
}

const PathNode = ({ level, status, alignment }) => {
  const alignmentClass = 
    alignment === 'left' ? "alignLeft" : 
    alignment === 'right' ? "alignRight" : 
    "alignCenter";

  const nodeStyle = status === 'active' ? "activeNode" :
  status === 'completed' ? "completedNode" :
   "lockedNode";

  return (
    <div className={`${"nodeContainer"} ${alignmentClass}`}>
      <button className={`${"nodeButton"} ${nodeStyle}`}></button>
      <span className={"levelText"}>Level {level}</span>
    </div>
  );
};

function PosterModal({ closeModal }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const levels = [
    { id: 1, status: 'completed', align: 'left' },
    { id: 2, status: 'completed', align: 'center' },
    { id: 3, status: 'completed', align: 'right' },
    { id: 4, status: 'completed', align: 'center' },
    { id: 5, status: 'active', align: 'left' },
    { id: 6, status: 'locked', align: 'center' },
    { id: 7, status: 'locked', align: 'right' },
    { id: 8, status: 'locked', align: 'center' },
    { id: 9, status: 'locked', align: 'left' },
    { id: 10, status: 'locked', align: 'center' },
  ];

  return createPortal(
    <div className="modalBackground">
      <div className="modalWindow">
        <div className="closeModal">
          <button 
            onClick={() => {
              closeModal(null);
            }}
          >
            [ X ]
          </button>
        </div>
        <h2 className="header">
          Growth Path
        </h2>
        <div className="infoBanner">
          Keep logging in, completing daily and weekly quests to unlock more levels and unlock more items for your room!
        </div>
        <div className="pathContainer">
          {levels.map((level) => (
            <PathNode 
              key={level.id} 
              level={level.id} 
              status={level.status} 
              alignment={level.align} 
            />
          ))}
        </div>
      </div>
    </div>,
    document.body
  );
}

function LaptopModal( {closeModal} ) {
  return( 
    <div className="modalBackground">
      <div className="modalWindow">
        <div className="closeModal">
          <button 
            onClick={() => {
              closeModal(null);
            }}
          >
            [ X ]
          </button>
        </div>
        <Hub />
      </div>
    </div>
  )
}

const QuestCard = ({ quest, onComplete }) => {
  const clickable = !quest.completed && !quest.auto;
  return (
    <div
      className={`${"questCard"} ${quest.completed ? "questCardCompleted" : ''}`}
      onClick={() => clickable && onComplete(quest.key)}
    >
      <div className={`${"circle"} ${quest.completed ? "circleCompleted" : ''}`}></div>
      <span className={`${"questText"} ${quest.completed ? "questTextCompleted" : ''}`}>
        {quest.label} (+ {quest.xp} EXP)
      </span>
    </div>
  );
}

function BookModal({ closeModal, onLevelChange }) {
  const [quests, setQuests] = useState([]);
  const [levelUpInfo, setLevelUpInfo] = useState(null);

  const loadQuests = async () => {
    try {
      const data = await getQuests();
      setQuests(data.quests);
    } catch (err) {
      console.error("couldnt load quests", err);
    }
  };

  useEffect(() => {
    loadQuests();
  }, []);

  const handleComplete = async (questKey) => {
    try {
      const result = await completeQuest(questKey);
      if (result.leveled_up) {
        setLevelUpInfo({ level: result.new_level, furniture: result.furniture });
        if (onLevelChange) onLevelChange();
      }
      await loadQuests();
    } catch (err) {
      console.error("quest completion failed", err);
    }
  };

  const dailyQuests = quests.filter(q => q.period === 'daily');
  const weeklyQuests = quests.filter(q => q.period === 'weekly');

  return(
    <div className="modalBackground">
      <div className="modalWindow">
        <div className="closeModal">
          <button
            onClick={() => {
              closeModal(null);
            }}
          >
            [ X ]
          </button>
        </div>
        <h2 className="header">
          Quests!
        </h2>
        <h3 className="sectionTitle">
          Daily
        </h3>
        <div>
        {dailyQuests.map((quest) => (
          <QuestCard
            key={quest.key}
            quest={quest}
            onComplete={handleComplete}
          />
        ))}
        </div>
        <h3 className="sectionTitle">
          Weekly
        </h3>
        <div>
        {weeklyQuests.map((quest) => (
          <QuestCard
            key={quest.key}
            quest={quest}
            onComplete={handleComplete}
          />
        ))}
        </div>
      </div>
      <LevelUpModal
        isOpen={levelUpInfo !== null}
        newLevel={levelUpInfo?.level}
        unlockedItem={levelUpInfo?.furniture}
        onClose={() => setLevelUpInfo(null)}
      />
    </div>
  );
}


export default function Room() {
  const [activeModal, setActiveModal] = useState(null);
  const [level, setLevel] = useState(0);
  const [animation, setAnimation] = useState('Idle');

  const refreshLevel = () => {
    getRoom().then(data => setLevel(data.level)).catch(() => {});
  };

  useEffect(() => {
    refreshLevel();
  }, []);

  const levelUp = () => setLevel(prevLevel => prevLevel + 1)
  const levelDown = () => setLevel(prevLevel => Math.max(0, prevLevel - 1))

  useEffect(() => {
    const walkTimer = setInterval(() => {
      setAnimation('Walk');
      setTimeout(() => {
        setAnimation('Idle');
      }, 10000);

    }, 25000);

    return () => clearInterval(walkTimer);
  }, []);

  return (
      <div className="simple-page">
        <NavBar />
        <div style={{ position: 'absolute', zIndex: 1, padding: '20px' }}>
        <button 
          onClick={() => {
            levelDown();
            setAnimation('Sad');
          }}
        >
          Level Down
        </button>
        <span style={{ margin: '0 15px', color: 'white' }}>Current Level: {level}</span>
        <button 
          onClick={() => {
            levelUp();
            setAnimation('Happy');
          }}
        >
          Level Up
        </button>      
      </div>
      <div id="canvas-container">
      <Canvas shadows camera={{position: [-2.86,3.62,4.80], rotation: [-0.39,0.38,0.15]}}>
        <Avatar currentAction={animation} />
        <Light />
        {level >= 1 && <AirMattress />}
        {level >= 6 && <Bookshelf />}
        {level >= 2 && <Chair />}
        {level >= 3 && <Desk />}
        {level >= 4 && <Lamp />}
        <Selection>
          <EffectComposer autoClear={false}>
            <Outline blur visibleEdgeColor="white" edgeStrength={10} width={1000} />
          </EffectComposer>
          <Laptop onLaptopClick={() => setActiveModal('laptop')}/>
          <Poster onPosterClick={() => setActiveModal('poster')}/>
          <Book onBookClick={() => setActiveModal('book')}/>
        </Selection>
        {level >= 8 && <Plant />}
        <Environment />
        {level >= 9 && <Rug />}
        {level >= 7 && <Window />}
      </Canvas>

      {activeModal === 'poster' && <PosterModal closeModal={setActiveModal} /> }
      {activeModal === 'laptop' && <LaptopModal closeModal={setActiveModal} />}
      {activeModal === 'book' && <BookModal closeModal={setActiveModal} onLevelChange={refreshLevel} />}

    </div>

    </div>
  );
}
