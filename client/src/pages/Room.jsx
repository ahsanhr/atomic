import NavBar from "../components/Navbar";
import Hub from "./Hub.jsx"
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

import { getTip } from "../api";

function Tip() {
  const [tip, setTip] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  async function loadTip() {
    try {
      const data = {
        income: 5000,
        expenses: 3000,
        savings: 500
      };
      
      const response = await getTip(data);
      
      setTip(response.daily_tip); 
      
    } catch (error) {
      console.log(error.message);
      setTip("Failed to load tip.");
    } 
  }

  return (
    <div className="tip-container">
      <button onClick={loadTip} disabled={isLoading} children className="infoBanner">
        {isLoading ? "Generating..." : "Get a financial tip from Atomo!"}
      </button>
      {tip && (
        <p>{tip}</p>
      )}
    </div>
  );
}

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

function Friend() {
  const friendRef = useRef()
  const { scene, animations }  = useGLTF("/friend.glb");
  const { actions, names } = useAnimations(animations, friendRef);

  useEffect(()=> {
    const action = actions['FriendIdle'];

    action.reset().fadeIn(0.5).play();

    return () => action.fadeOut(0.5);
  }, [actions]);

  return (
    <group ref={friendRef} dispose={null}>
      <primitive object={scene} position={[-2, 0, -2]} />
    </group>
  )

}

function AvatarModal( {closeModal} ) {
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
            <Tip />
      </div>
    </div>
  )

}

function Avatar({currentAction, onAvatarClick}) {
  const group = useRef();

  const [hovered, setHovered] = useState(false);

  const { scene, animations } = useGLTF('/avatar.glb');
  const { actions } = useAnimations(animations, group);
  

  const walkTimer = useRef(0);
  const moveSpeed = 2; 
  const startZ = 0;

  useEffect(() => {
    const action = actions[currentAction];
    if (!action) return;

    action.reset().fadeIn(0.5).play();

    // forces Happy and Sad to play exactly one time and stop
    if (currentAction === 'Happy' || currentAction === 'Sad') {
      action.setLoop(THREE.LoopOnce, 1);
      action.clampWhenFinished = true; 
    } else {
      // Walk and Idle should loop normally
      action.setLoop(THREE.LoopRepeat, Infinity);
    }

    return () => action.fadeOut(0.5);
  }, [currentAction, actions]);

  useFrame((state, delta) => {
    if (!group.current) return;

    if (currentAction === 'Walk') {
      // Add the time passed since last frame
      walkTimer.current += delta;
      
      // First 1.5 seconds: Walk forward on Z
      if (walkTimer.current <= 1) {
        group.current.position.z += moveSpeed * delta;
        group.current.rotation.y = 0; // Face forward
      } 
      // Next 1.5 seconds: Turn around and walk back
      else if (walkTimer.current <= 2) {
        group.current.position.z -= moveSpeed * delta;
        group.current.rotation.y = Math.PI; // Turn 180 degrees (Math.PI is half a circle)
      }
    } else {
      // Not walking? Reset everything so he's ready for the next 10-second trigger
      walkTimer.current = 0;
      group.current.position.z = startZ; // Snap exactly to start to prevent drifting
      group.current.rotation.y = 0;      // Face forward for Idle/Happy/Sad
    }
  });

  useEffect(() => {
    scene.traverse((child) => {
      if (child.isMesh && child.material) {
        child.material.transparent = false;
        child.material.depthWrite = true;
      }
    });
  }, [scene]);

  return (
    <Select enabled={hovered}>
      <group ref={group} dispose={null}>
        <primitive 
        object={scene} 
                onClick={(e) => {
          e.stopPropagation();
          onAvatarClick();
        }}
        onPointerEnter={(e) => {
          e.stopPropagation(); 
          setHovered(true);
        }}
        onPointerLeave={() => setHovered(false)} 
        />
      </group>
    </Select>
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

const QuestCard = ({quest, onToggle}) => {
  return (
    <div 
      className={`${"questCard"} ${quest.completed ? "questCardCompleted" : ''}`}
      onClick={() => onToggle(quest.id)}
      >
        <div className={`${"circle"} ${quest.completed ? "circleCompleted" : ''}`}></div>       
        <span className={`${"questText"} ${quest.completed ? "questTextCompleted" : ''}`}>
          {quest.text} (+ {quest.exp} EXP)
        </span>
    </div>
  )
}

function BookModal( {closeModal} ) {
  const [quests, setQuests] = useState([
    { id: 1, type: 'daily', text: 'check your daily transactions!', exp: 50, completed: false },
    { id: 2, type: 'daily', text: 'look at the daily finance tip!', exp: 20, completed: false },
    { id: 3, type: 'weekly', text: 'input a savings goal!', exp: 100, completed: false },
    { id: 4, type: 'weekly', text: 'login 7 times this week!', exp: 150, completed: false },
    { id: 5, type: 'weekly', text: 'make your own coffee 4x this week', exp: 80, completed: false },
  ]);

  const toggleQuest = (id) => {
    setQuests((prevQuests) =>
      prevQuests.map((quest) =>
        quest.id === id ? { ...quest, completed: !quest.completed } : quest
      )
    );
  };

  const dailyQuests = quests.filter(q => q.type === 'daily');
  const weeklyQuests = quests.filter(q => q.type === 'weekly');

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
            key={quest.id} 
            quest={quest} 
            onToggle={toggleQuest} 
          />
        ))}
      </div>
        <h3 className="sectionTitle">
          Weekly
        </h3>
        <div>
        {weeklyQuests.map((quest) => (
          <QuestCard 
            key={quest.id} 
            quest={quest} 
            onToggle={toggleQuest} 
          />
        ))}
      </div>
      </div>
    </div>
  )
}


export default function Room() {
  const [activeModal, setActiveModal] = useState(null);
  const [level, setLevel] = useState(0);

  const levelUp = () => setLevel(prevLevel => prevLevel + 1)
  const levelDown = () => setLevel(prevLevel => Math.max(0, prevLevel - 1))

  const [animation, setAnimation] = useState('Idle');

  const playReaction = (animName) => {
    setAnimation(animName);
  
    setTimeout(() => {
      setAnimation('Idle');
    }, 7000); 
  };

  useEffect(() => {
    const walkTimer = setInterval(() => {
      setAnimation('Walk');
      setTimeout(() => {
        setAnimation('Idle');
      }, 2000);

    }, 10000);

    return () => clearInterval(walkTimer);
  }, []);
  
  return (
      <div className="simple-page">
        <NavBar />
        <div style={{ position: 'absolute', zIndex: 1, padding: '20px' }}>
          <button onClick={() => { levelDown(); playReaction('Sad'); }}>
            Level Down
          </button>        
          <span style={{ margin: '0 15px', color: 'white' }}>Current Level: {level}</span>
          <button onClick={() => { levelUp(); playReaction('Happy'); }}>
            Level Up
          </button>
      </div>
      <div id="canvas-container">
      <Canvas shadows camera={{position: [-2.86,3.62,4.80], rotation: [-0.39,0.38,0.15]}}>
        <Light />
        {level >= 1 && <AirMattress />}
        {level >= 6 && <Bookshelf />}
        {level >= 2 && <Chair />}
        {level >= 3 && <Desk />}
        {level >= 4 && <Lamp />}
        {level >= 5 && <Friend />}
        <Selection>
          <EffectComposer autoClear={false} depthBuffer={true}>
            <Outline blur visibleEdgeColor="white" edgeStrength={10} width={1000} />
          </EffectComposer>
          <Laptop onLaptopClick={() => setActiveModal('laptop')}/>
          <Poster onPosterClick={() => setActiveModal('poster')}/>
          <Book onBookClick={() => setActiveModal('book')}/>
          <Avatar onAvatarClick={() => setActiveModal('tip')} currentAction={animation} />
        </Selection>
        {level >= 8 && <Plant />}
        <Environment />
        {level >= 9 && <Rug />}
        {level >= 7 && <Window />}
      </Canvas>

      {activeModal === 'poster' && <PosterModal closeModal={setActiveModal} /> }
      {activeModal === 'laptop' && <LaptopModal closeModal={setActiveModal} />}
      {activeModal === 'book' && <BookModal closeModal={setActiveModal} />}
      {activeModal === 'tip' && <AvatarModal closeModal={setActiveModal} />}
    </div>

    </div>
  );
}
