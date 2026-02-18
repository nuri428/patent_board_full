# Patent Board Frontend - Developer & Agent Guide

## 1. 📋 프로젝트 설명 (Project Description)
본 섹션은 Patent Board의 사용자 인터페이스를 담당하는 React 기반 프론트엔드 프로젝트입니다. Vite를 빌드 도구로 사용하며, Tailwind CSS를 통해 현대적이고 반응형인 디자인을 구현합니다.

## 2. 💻 설치 및 개발 환경 (Setup & Dev Environment)
- **런타임**: Node.js 20+
- **패키지 매니저**: `npm`
- **초기화**: `npm install`을 통해 의존성을 설치합니다.
- **환경 설정**: `.env` 파일에 API 엔드포인트(`VITE_API_URL`) 설정 필요.

## 3. 🚀 빌드/테스트/런 명령어 (Commands)
- **개발 서버**: `npm run dev`
- **빌드**: `npm run build`
- **린트**: `npm run lint`
- **E2E 테스트**: `npm run test:e2e`

## 4. 📏 코드 스타일 & 컨벤션 (Conventions)
- **컴포넌트 구조**: 함수형 컴포넌트와 Hook(`useState`, `useEffect`)을 기본으로 사용합니다.
- **스타일링**: Tailwind CSS 유틸리티 클래스를 사용하여 스타일을 정의합니다.
- **상태 관리**: 복잡한 전역 상태는 `zustand`를 사용하여 관리합니다.
- **API 통신**: `axios`를 사용하며, API 호출 로직은 전용 Hook이나 서비스 레이어로 분리합니다.

## 5. 🏗️ 기술 스택 & 주요 폴더 구조 (Stack & Structure)
### 기술 스택
- **Library**: React 19
- **Build Tool**: Vite
- **Styling**: Tailwind CSS, Framer Motion (Animations)
- **Icons**: Lucide React
- **Visualization**: Chart.js, React-flow (Graph UI)

### 폴더 구조
- `src/components/`: 재사용 가능한 UI 컴포넌트
- `src/pages/`: 라우트별 페이지 컴포넌트
- `src/hooks/`: 커스텀 훅
- `src/store/`: Zustand 상태 저장소
- `src/api/`: API 클라이언트 및 엔드포인트 정의

## 6. 🤖 기대 행동 & 역할 정의 (Role Definition)
- **반응형 디자인**: 모든 새로운 UI 요소는 모바일과 데스크탑 환경을 모두 지원해야 합니다.
- **컴포넌트 재사용**: 공통 UI 요소는 `components` 폴더에 추상화하여 중복을 최소화합니다.
- **사용자 경험(UX)**: 로딩 상태, 에러 피드백 등 적절한 사용자 피드백을 반드시 고려해야 합니다.

## 7. 🚫 금지 규칙 (Prohibited Rules)
- **인라인 스타일 지양**: 가급적 Tailwind 클래스를 사용하고 복잡한 경우 CSS 모듈을 사용합니다.
- **직접 DOM 조작 금지**: React의 선언적 패턴을 따르며 `document.querySelector` 등을 사용하지 않습니다.
- **Prop Drilling 지양**: 깊은 단계의 데이터 전달은 Context API 또는 Zustand를 활용합니다.

## 8. 📚 참조 문서 링크 & 단서 (References)
- **전체 가이드**: [../AGENTS.md](file:///home/nuri/dev/git/patent_board_full/AGENTS.md)
- **디자인 시스템**: `LANDING_PAGE.md` (프로젝트 루트 참고)
