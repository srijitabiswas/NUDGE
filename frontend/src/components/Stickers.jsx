// Hand-drawn style sticker cluster for the landing CTA. Pure SVG, no text.
const INK = "#2b2118";
const CREAM = "#fbf3e4";
const TEAL = "#2f8f8a";
const CORAL = "#ee9b8c";
const YELLOW = "#f2bd4b";
const SAGE = "#6f9c8d";
const SKIN = "#f2c4a0";
const HAIR = "#3a2d22";
const P = { stroke: INK, strokeWidth: 3, strokeLinejoin: "round", strokeLinecap: "round" };

const Spark = ({ x, y, s = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <path d="M0 -16C2 -6 6 -2 16 0C6 2 2 6 0 16C-2 6 -6 2 -16 0C-6 -2 -2 -6 0 -16Z" fill={YELLOW} {...P} strokeWidth={2.5} />
  </g>
);

export default function Stickers() {
  return (
    <svg className="ld-stk" viewBox="0 0 720 560" fill="none" role="img" aria-label="Illustrated stickers: a message, a task card, a bell, a calendar, a notebook and a happy student">
      <defs>
        <filter id="stk" x="-30%" y="-30%" width="160%" height="160%">
          <feMorphology in="SourceAlpha" operator="dilate" radius="5" result="d" />
          <feFlood floodColor="#faf7f2" result="w" />
          <feComposite in="w" in2="d" operator="in" result="o" />
          <feGaussianBlur in="d" stdDeviation="4" result="b" />
          <feOffset in="b" dy="5" result="bo" />
          <feFlood floodColor="#000" floodOpacity="0.35" result="sh" />
          <feComposite in="sh" in2="bo" operator="in" result="s" />
          <feMerge><feMergeNode in="s" /><feMergeNode in="o" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      {/* message bubble */}
      <g transform="translate(14 22) rotate(-3)">
        <g className="st st1" filter="url(#stk)">
          <path d="M40 0H220A40 40 0 0 1 260 40V110A40 40 0 0 1 220 150H112L62 196L72 150H40A40 40 0 0 1 0 110V40A40 40 0 0 1 40 0Z" fill={CREAM} {...P} />
          <circle cx="44" cy="52" r="22" fill={TEAL} {...P} />
          <circle cx="44" cy="46" r="7" fill={CREAM} />
          <path d="M31 64C33 54 55 54 57 64" fill={CREAM} />
          <rect x="82" y="34" width="150" height="9" rx="4.5" fill={INK} opacity="0.75" />
          <rect x="82" y="58" width="120" height="9" rx="4.5" fill={INK} opacity="0.75" />
          <rect x="82" y="82" width="140" height="9" rx="4.5" fill={INK} opacity="0.75" />
          <path d="M90 116C104 108 118 124 132 116C146 108 160 124 174 116" stroke={CORAL} strokeWidth="4" strokeLinecap="round" />
          <circle cx="250" cy="8" r="23" fill={CORAL} {...P} />
          <rect x="246" y="-5" width="8" height="15" rx="4" fill={CREAM} />
          <circle cx="250" cy="19" r="4.5" fill={CREAM} />
        </g>
      </g>

      {/* arrow */}
      <g className="st st2">
        <path d="M92 232C96 290 150 312 222 296" stroke={TEAL} strokeWidth="6" strokeLinecap="round" strokeDasharray="11 10" />
        <path d="M214 276L246 298L212 316Z" fill={TEAL} {...P} strokeWidth={2.5} />
      </g>

      {/* task card */}
      <g transform="translate(252 112) rotate(2)">
        <g className="st st3" filter="url(#stk)">
          <rect x="8" y="10" width="220" height="290" rx="22" fill="#e6d6bd" {...P} />
          <rect x="0" y="0" width="220" height="290" rx="22" fill={CREAM} {...P} />
          <rect x="62" y="-16" width="104" height="32" rx="3" fill={CORAL} opacity="0.85" transform="rotate(-2 114 0)" />
          {[52, 88, 124, 160, 196, 232, 268].map((y) => (
            <ellipse key={y} cx="2" cy={y} rx="8" ry="6" fill="#d9c9b0" {...P} strokeWidth={2.5} />
          ))}
          <circle cx="44" cy="44" r="17" fill={TEAL} {...P} />
          <path d="M36 44L42 50L53 37" stroke={CREAM} strokeWidth="4.5" strokeLinecap="round" strokeLinejoin="round" />
          <rect x="72" y="38" width="96" height="12" rx="6" fill={INK} />
          <path d="M72 62H190" stroke={CORAL} strokeWidth="3.5" strokeLinecap="round" />
          <Spark x={196} y={34} s={0.55} />
          {[
            { y: 96, c: CORAL },
            { y: 134, c: INK },
            { y: 172, c: YELLOW },
            { y: 210, c: CORAL },
          ].map(({ y, c }, i) => (
            <g key={y}>
              {i === 0 && <rect x="30" y={y - 10} width="20" height="20" rx="4" fill="none" {...P} strokeWidth={2.5} />}
              {i === 1 && <path d="M32 134L42 124H50V132L40 142Z" fill="none" {...P} strokeWidth={2.5} />}
              {i === 2 && <circle cx="40" cy={y} r="10" fill="none" {...P} strokeWidth={2.5} />}
              {i === 3 && <path d="M32 220V200H50L45 206L50 212H34" fill={YELLOW} {...P} strokeWidth={2.5} />}
              <rect x="66" y={y - 6} width="44" height="8" rx="4" fill={INK} opacity="0.6" />
              <rect x="120" y={y - 6} width="64" height="8" rx="4" fill={c} />
            </g>
          ))}
          <path d="M26 240H196" stroke={INK} strokeWidth="2.5" strokeDasharray="7 6" opacity="0.5" />
          <rect x="30" y="256" width="22" height="22" rx="4" fill={CREAM} {...P} strokeWidth={2.5} />
          <path d="M34 266L40 272L52 256" stroke={TEAL} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
          <rect x="66" y="262" width="84" height="9" rx="4.5" fill={INK} opacity="0.7" />
          <path d="M184 270C170 262 170 252 178 250C182 249 184 252 184 254C184 252 188 249 192 250C200 252 198 262 184 270Z" fill={CORAL} {...P} strokeWidth={2} />
        </g>
      </g>

      {/* bell */}
      <g transform="translate(506 6) rotate(10)">
        <g className="st st4" filter="url(#stk)">
          <circle cx="40" cy="4" r="7" fill={YELLOW} {...P} strokeWidth={2.5} />
          <path d="M2 74C2 36 16 10 40 10C64 10 78 36 78 74L94 92H-14Z" fill={YELLOW} {...P} />
          <path d="M16 64C16 44 22 28 34 22" stroke="#fff6d6" strokeWidth="5" strokeLinecap="round" />
          <circle cx="40" cy="100" r="10" fill={YELLOW} {...P} strokeWidth={2.5} />
          <circle cx="72" cy="14" r="15" fill={CORAL} {...P} strokeWidth={2.5} />
          <rect x="69" y="6" width="6" height="16" rx="3" fill={CREAM} />
        </g>
      </g>
      <Spark x={472} y={46} s={0.8} />
      <Spark x={628} y={30} s={0.5} />

      {/* calendar */}
      <g transform="translate(486 196) rotate(5)">
        <g className="st st5" filter="url(#stk)">
          <path d="M146 8L176 28V122L146 134Z" fill="#d9c9b0" {...P} />
          <rect x="0" y="0" width="150" height="134" rx="10" fill={CREAM} {...P} />
          <path d="M0 10A10 10 0 0 1 10 0H140A10 10 0 0 1 150 10V32H0Z" fill={TEAL} {...P} />
          {[26, 56, 86, 116].map((x) => (
            <rect key={x} x={x} y="-12" width="9" height="26" rx="4.5" fill={CREAM} {...P} strokeWidth={2.5} />
          ))}
          <path d="M0 62H150M0 92H150M30 32V134M60 32V134M90 32V134M120 32V134" stroke={INK} strokeWidth="1.8" opacity="0.28" />
          <circle cx="75" cy="78" r="13" stroke={CORAL} strokeWidth="4" />
          <Spark x={134} y={112} s={0.62} />
        </g>
      </g>

      {/* notebook + pencil */}
      <g transform="translate(18 330) rotate(-8)">
        <g className="st st6" filter="url(#stk)">
          <rect x="0" y="0" width="122" height="156" rx="12" fill={SAGE} {...P} />
          {[22, 44, 66, 88, 110, 132].map((y) => (
            <circle key={y} cx="10" cy={y} r="5.5" fill={CREAM} {...P} strokeWidth={2} />
          ))}
          <rect x="32" y="22" width="66" height="40" rx="6" fill={CREAM} {...P} strokeWidth={2.5} />
          <path d="M98 128C84 120 84 108 92 106C96 105 98 108 98 110C98 108 102 105 106 106C114 108 112 120 98 128Z" fill={CORAL} {...P} strokeWidth={2} />
        </g>
      </g>
      <g transform="translate(160 318) rotate(14)">
        <g className="st st2" filter="url(#stk)">
          <rect x="0" y="-22" width="28" height="26" rx="5" fill={CORAL} {...P} />
          <rect x="0" y="2" width="28" height="10" fill="#cfd3d6" {...P} strokeWidth={2.5} />
          <rect x="0" y="12" width="28" height="138" fill={YELLOW} {...P} />
          <path d="M9 12V150M19 12V150" stroke="#c98f1c" strokeWidth="2" />
          <path d="M0 150H28L14 186Z" fill={SKIN} {...P} />
          <path d="M9 170H19L14 186Z" fill={INK} />
        </g>
      </g>

      {/* grad cap */}
      <g transform="translate(236 436) rotate(-4)">
        <g className="st st3" filter="url(#stk)">
          <path d="M26 44V78Q75 104 124 78V44L75 62Z" fill={HAIR} {...P} />
          <path d="M0 30L75 0L150 30L75 60Z" fill="#37363c" {...P} />
          <path d="M75 30L132 40V82" stroke={YELLOW} strokeWidth="4" strokeLinecap="round" />
          <rect x="126" y="80" width="12" height="22" rx="4" fill={YELLOW} {...P} strokeWidth={2.5} />
        </g>
      </g>

      {/* sticky note */}
      <g transform="translate(396 396) rotate(-5)">
        <g className="st st4" filter="url(#stk)">
          <path d="M0 0H100V76L76 100H0Z" fill="#f4b9a8" {...P} />
          <path d="M100 76L76 100V76Z" fill="#e39a88" {...P} strokeWidth={2.5} />
          <rect x="30" y="-12" width="44" height="22" rx="3" fill={YELLOW} opacity="0.9" />
          <circle cx="34" cy="46" r="4.5" fill={INK} />
          <circle cx="66" cy="46" r="4.5" fill={INK} />
          <path d="M32 62Q50 80 68 62" stroke={INK} strokeWidth="3.5" strokeLinecap="round" />
        </g>
      </g>

      {/* paperclip */}
      <g transform="translate(668 168) rotate(18)">
        <g className="st st1" filter="url(#stk)">
          <path d="M16 70V22C16 6 40 6 40 22V80C40 98 4 98 4 78V30" stroke={TEAL} strokeWidth="6" strokeLinecap="round" />
        </g>
      </g>

      {/* happy student */}
      <g transform="translate(546 338)">
        <g className="st st5" filter="url(#stk)">
          <path d="M-6 190C-6 142 26 114 70 114C114 114 146 142 146 190Z" fill={TEAL} {...P} />
          <path d="M52 114L70 136L88 114" stroke={INK} strokeWidth="3" fill={CREAM} strokeLinejoin="round" />
          <path d="M60 140V156M80 140V156" stroke={CREAM} strokeWidth="3" strokeLinecap="round" />
          <path d="M-2 160C-26 138 -30 110 -18 84" stroke={TEAL} strokeWidth="24" strokeLinecap="round" />
          <path d="M-2 160C-26 138 -30 110 -18 84" stroke={INK} strokeWidth="3" strokeLinecap="round" opacity="0" />
          <circle cx="-18" cy="76" r="12" fill={SKIN} {...P} />
          <rect x="58" y="92" width="24" height="28" rx="8" fill={SKIN} {...P} />
          <circle cx="70" cy="62" r="43" fill={SKIN} {...P} />
          <path d="M26 62C20 20 54 4 82 8C112 12 122 38 114 64C106 44 90 38 70 40C50 42 34 48 26 62Z" fill={HAIR} {...P} />
          <circle cx="44" cy="76" r="8" fill={CORAL} opacity="0.55" />
          <circle cx="96" cy="76" r="8" fill={CORAL} opacity="0.55" />
          <path d="M48 62Q55 53 62 62" stroke={INK} strokeWidth="3.5" strokeLinecap="round" />
          <path d="M78 62Q85 53 92 62" stroke={INK} strokeWidth="3.5" strokeLinecap="round" />
          <path d="M50 76Q70 100 90 76Z" fill="#fff" {...P} strokeWidth={3} />
          <path d="M60 87Q70 94 80 87" stroke={CORAL} strokeWidth="4" strokeLinecap="round" />
        </g>
      </g>
      <Spark x={668} y={344} s={0.7} />
      <Spark x={524} y={330} s={0.5} />
    </svg>
  );
}