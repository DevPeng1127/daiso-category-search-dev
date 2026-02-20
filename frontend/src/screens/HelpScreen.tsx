import Logo from '../components/Logo';
import BottomNav from '../components/BottomNav';

const sections = [
  {
    title: '검색 방법',
    content: '마이크 버튼을 눌러 음성으로 검색하거나, 텍스트를 직접 입력하여 검색할 수 있습니다.',
  },
  {
    title: '검색 예시',
    content: '"욕실 슬리퍼", "요가 매트", "세탁세제 위치 알려줘" 등 찾으시는 상품명이나 카테고리를 말씀해 주세요.',
  },
  {
    title: '결과 확인',
    content: '검색 결과에서 최대 3개의 상품이 표시되며, BEST 마크가 붙은 상품이 가장 관련도가 높은 상품입니다.',
  },
  {
    title: '길안내',
    content: '상품을 선택하면 매장 지도에서 해당 상품까지의 경로를 안내해 드립니다.',
  },
  {
    title: 'QR 이용',
    content: '지도 화면의 QR코드를 스캔하면 스마트폰으로 위치 정보를 확인하실 수 있습니다.',
  },
];

export default function HelpScreen() {
  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="px-8 pt-6 pb-2">
        <Logo />
      </header>

      {/* Title */}
      <h2 className="text-center text-2xl font-extrabold text-daiso-gray-900 mb-6">
        도움말
      </h2>

      {/* Content */}
      <main className="flex-1 overflow-y-auto px-8 pb-8">
        <div className="max-w-2xl mx-auto space-y-6">
          {sections.map((section, i) => (
            <div key={i} className="bg-gray-50 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-daiso-gray-900 mb-2">
                {section.title}
              </h3>
              <p className="text-base text-gray-600 leading-relaxed">
                {section.content}
              </p>
            </div>
          ))}
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
