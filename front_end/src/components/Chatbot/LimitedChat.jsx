import React, { useState } from 'react';
import PropTypes from 'prop-types';

function LimitedChat({ onGetStarted }) {
    const [showFeatures, setShowFeatures] = useState(false);

    const limitedFeatures = [
        {
            title: "기능 제한 안내",
            description: "로그인하시면 모든 기능을 사용할 수 있습니다.",
            icon: (
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
            )
        },
        {
            title: "제공되는 기능",
            description: "로그인 전에는 기능이 제한됩니다.",
            icon: (
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            )
        },
        {
            title: "로그인 후 혜택",
            description: "완전한 특허 분석 기능을 이용할 수 있습니다.",
            icon: (
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            )
        }
    ];

    const handleSendMessage = () => {
        alert("로그인 후에만 채팅 기능을 사용할 수 있습니다. '시작하기' 버튼을 눌러 로그인해주세요.");
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
            <div className="max-w-4xl w-full">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="flex justify-center mb-4">
                        <div className="bg-gradient-to-r from-yellow-500 to-orange-500 p-4 rounded-2xl shadow-lg">
                            <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                        </div>
                    </div>
                    <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                        특허 분석 챗봇 데모
                    </h1>
                    <p className="text-lg text-gray-600 mb-6">
                        로그인 전 제한된 기능으로 플랫폼을 체험해보세요
                    </p>
                </div>

                {/* Limited Chat Interface */}
                <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
                    <div className="mb-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-2">
                            간단한 안내 채팅
                        </h2>
                        <p className="text-gray-600">
                            로그인 전에는 기본 안내 기능만 제공됩니다. 특허 분석 등 완전한 기능은 로그인 후 이용할 수 있습니다.
                        </p>
                    </div>

                    {/* Chat Window */}
                    <div className="border border-gray-200 rounded-lg h-64 p-4 mb-4 overflow-y-auto">
                        <div className="space-y-4">
                            {/* Welcome Message */}
                            <div className="flex justify-start">
                                <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg max-w-md">
                                    <p className="text-sm">안녕하세요! 특허 분석 챗봇 데모입니다. 로그인 후 완전한 기능을 이용할 수 있습니다.</p>
                                    <p className="text-xs text-blue-600 mt-1">현재: 제한된 모드</p>
                                </div>
                            </div>

                            {/* User Message */}
                            <div className="flex justify-end">
                                <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg max-w-md">
                                    <p className="text-sm">이 서비스는 어떤 기능을 제공하나요?</p>
                                </div>
                            </div>

                            {/* Bot Response */}
                            <div className="flex justify-start">
                                <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg max-w-md">
                                    <p className="text-sm">저희 서비스는 AI 기반 특허 분석을 제공합니다. 로그인 후에는 다음과 같은 기능을 이용할 수 있습니다:</p>
                                    <ul className="text-xs mt-2 space-y-1">
                                        <li>• 전체 특허 데이터베이스 검색</li>
                                        <li>• AI 기반 특허 분석</li>
                                        <li>• 상세 분석 보고서 생성</li>
                                        <li>• 맞춤형 추천 기능</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Input Area */}
                    <div className="flex gap-2">
                        <button
                            onClick={handleSendMessage}
                            className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
                            disabled
                        >
                            <span className="text-sm">로그인 후 사용 가능</span>
                        </button>
                    </div>
                </div>

                {/* Features Overview */}
                <div className="mb-8">
                    <div className="text-center mb-6">
                        <button
                            onClick={() => setShowFeatures(!showFeatures)}
                            className="text-blue-600 hover:text-blue-800 font-medium flex items-center justify-center mx-auto"
                        >
                            {showFeatures ? '숨기기' : '자세히 알아보기'}
                            <svg className={`w-4 h-4 ml-2 transform transition-transform ${showFeatures ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                    </div>

                    {showFeatures && (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {limitedFeatures.map((feature, index) => (
                                <div key={index} className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
                                    <div className="mb-4">{feature.icon}</div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                                    <p className="text-gray-600 text-sm">{feature.description}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* CTA Section */}
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">
                        완전한 기능을 이용해보세요
                    </h2>
                    <p className="text-gray-600 mb-6">
                        로그인하면 모든 특허 분석 기능을 무료로 사용할 수 있습니다
                    </p>
                    
                    <button
                        onClick={onGetStarted}
                        className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl text-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 mb-4"
                    >
                        로그인 / 시작하기
                    </button>
                    
                    <p className="text-sm text-gray-500">
                        간단한 데모 로그인입니다. 실제 이메일/비밀번호가 필요하지 않습니다
                    </p>
                </div>
            </div>
        </div>
    );
}

LimitedChat.propTypes = {
    onGetStarted: PropTypes.func.isRequired
};

export default LimitedChat;